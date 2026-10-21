"""
PharmaLeaf AI - Multi-Column Layout Analyzer & Reading Order Engine
Specialized for dense pharmaceutical leaflets with 1, 2, or 3 columns,
proper RTL/LTR column ordering, table recognition, heading tagging, and dosage protection.
"""
import re
from typing import Any
from .constants import PHARMA_SECTIONS, DOSAGE_PATTERN, LOW_CONFIDENCE_THRESHOLD


class LayoutAnalyzer:
    def __init__(self, page_width: int, page_height: int):
        self.page_width = max(1, page_width)
        self.page_height = max(1, page_height)

    @staticmethod
    def is_arabic_text(text: str) -> bool:
        """Determines if the text contains predominantly Arabic characters."""
        arabic_chars = sum(1 for c in text if '\u0600' <= c <= '\u06FF' or '\u0750' <= c <= '\u077F' or '\u08A0' <= c <= '\u08FF')
        latin_chars = sum(1 for c in text if 'a' <= c.lower() <= 'z')
        return arabic_chars >= latin_chars if (arabic_chars + latin_chars) > 0 else False

    def detect_columns(self, tokens: list[dict], min_column_width: int = 150) -> list[tuple[int, int]]:
        """
        Detects vertical column gutters by analyzing horizontal token distribution.
        Returns a list of (start_x, end_x) for each column, ordered Left to Right physically.
        """
        if not tokens:
            return [(0, self.page_width)]

        # Build horizontal occupancy histogram
        bins = np_histogram = [0] * (self.page_width + 1)
        for t in tokens:
            left, _, width, _ = t["bbox"]
            right = min(self.page_width, left + width)
            for x in range(max(0, left), right):
                bins[x] += 1

        # Smooth histogram with moving average
        kernel_size = 25
        smoothed = [0] * len(bins)
        for i in range(len(bins)):
            start_idx = max(0, i - kernel_size // 2)
            end_idx = min(len(bins), i + kernel_size // 2)
            smoothed[i] = sum(bins[start_idx:end_idx]) / (end_idx - start_idx)

        # Look for valleys where smoothed density is near zero between text peaks
        avg_density = sum(smoothed) / len(smoothed) if smoothed else 1.0
        valley_threshold = avg_density * 0.15

        valleys = []
        in_valley = False
        v_start = 0

        # Margin ignore zone (skip outer 5% on left and right)
        margin_x = int(self.page_width * 0.05)
        for x in range(margin_x, self.page_width - margin_x):
            if smoothed[x] <= valley_threshold:
                if not in_valley:
                    in_valley = True
                    v_start = x
            else:
                if in_valley:
                    in_valley = False
                    v_end = x
                    # A significant column gutter must be at least 25 pixels wide
                    if (v_end - v_start) >= 25:
                        valleys.append((v_start, v_end))

        # Only consider valleys that fall between actual text content (not page margins)
        min_text_x = min(t["bbox"][0] for t in tokens)
        max_text_x = max(t["bbox"][0] + t["bbox"][2] for t in tokens)

        valid_gutters = []
        for (vs, ve) in valleys:
            # Gutter must be well within text boundaries
            if vs > (min_text_x + 50) and ve < (max_text_x - 50):
                # Verify that there are tokens on BOTH the left and right of this gutter
                has_left = any((t["bbox"][0] + t["bbox"][2]) <= vs for t in tokens)
                has_right = any(t["bbox"][0] >= ve for t in tokens)
                if has_left and has_right:
                    valid_gutters.append((vs, ve))

        if not valid_gutters:
            return [(0, self.page_width)]

        # Enforce maximum of 3 columns for leaflets (max 2 gutters)
        if len(valid_gutters) > 2:
            # Sort valleys by width descending (most prominent gutters)
            sorted_gutters = sorted(valid_gutters, key=lambda v: (v[1] - v[0]), reverse=True)[:2]
            split_x_points = sorted([(vs + ve) // 2 for (vs, ve) in sorted_gutters])
        else:
            split_x_points = sorted([(vs + ve) // 2 for (vs, ve) in valid_gutters])

        columns = []
        curr_x = 0
        for sp in split_x_points:
            if (sp - curr_x) >= min_column_width:
                columns.append((curr_x, sp))
                curr_x = sp
        if (self.page_width - curr_x) >= min_column_width:
            columns.append((curr_x, self.page_width))

        return columns if columns else [(0, self.page_width)]

    def assign_tokens_to_columns(self, tokens: list[dict], column_boundaries: list[tuple[int, int]]) -> list[list[dict]]:
        """
        Assigns each token to its corresponding column based on horizontal center.
        """
        columns_tokens = [[] for _ in column_boundaries]
        for t in tokens:
            left, _, width, _ = t["bbox"]
            center_x = left + width / 2.0

            # Find matching column
            assigned = False
            for idx, (c_start, c_end) in enumerate(column_boundaries):
                if c_start <= center_x < c_end:
                    columns_tokens[idx].append(t)
                    assigned = True
                    break
            if not assigned:
                # Assign to closest column
                distances = [abs(center_x - (c_start + c_end) / 2) for (c_start, c_end) in column_boundaries]
                best_idx = distances.index(min(distances))
                columns_tokens[best_idx].append(t)

        return columns_tokens

    def group_tokens_into_lines(self, tokens: list[dict], is_arabic: bool) -> list[dict]:
        """
        Groups tokens within a column into coherent horizontal lines.
        Orders tokens inside each line based on reading direction (RTL for Arabic, LTR for English).
        """
        if not tokens:
            return []

        # Sort vertically by top coordinate
        sorted_tokens = sorted(tokens, key=lambda t: (t["bbox"][1], t["bbox"][0]))

        lines = []
        current_line_tokens = [sorted_tokens[0]]

        for t in sorted_tokens[1:]:
            _, top, _, height = t["bbox"]
            # Compare with vertical band of current line
            curr_tops = [tk["bbox"][1] for tk in current_line_tokens]
            curr_heights = [tk["bbox"][3] for tk in current_line_tokens]
            avg_top = sum(curr_tops) / len(curr_tops)
            avg_height = sum(curr_heights) / len(curr_heights)

            # If vertical overlap is sufficient (within 50% of line height)
            if abs(top - avg_top) <= (avg_height * 0.55):
                current_line_tokens.append(t)
            else:
                # Finish line and start new one
                lines.append(self._finalize_line(current_line_tokens, is_arabic))
                current_line_tokens = [t]

        if current_line_tokens:
            lines.append(self._finalize_line(current_line_tokens, is_arabic))

        return lines

    def _finalize_line(self, tokens: list[dict], is_arabic: bool) -> dict:
        """
        Sorts tokens inside a single line according to RTL or LTR and creates line metadata.
        """
        # Determine direction of this specific line
        line_text_sample = " ".join(t["text"] for t in tokens)
        line_is_arabic = self.is_arabic_text(line_text_sample) if line_text_sample else is_arabic

        if line_is_arabic:
            # Arabic reads right-to-left: tokens with higher X come first
            sorted_tokens = sorted(tokens, key=lambda t: t["bbox"][0], reverse=True)
        else:
            # English reads left-to-right: tokens with lower X come first
            sorted_tokens = sorted(tokens, key=lambda t: t["bbox"][0])

        full_text = " ".join(t["text"] for t in sorted_tokens)
        min_x = min(t["bbox"][0] for t in sorted_tokens)
        min_y = min(t["bbox"][1] for t in sorted_tokens)
        max_x = max(t["bbox"][0] + t["bbox"][2] for t in sorted_tokens)
        max_y = max(t["bbox"][1] + t["bbox"][3] for t in sorted_tokens)

        confidences = [t["confidence"] for t in sorted_tokens if t["confidence"] >= 0]
        avg_conf = (sum(confidences) / len(confidences)) if confidences else 0.0
        has_low_conf = any(t.get("is_low_confidence", False) for t in sorted_tokens)

        # Detect dosages and measurements
        dosages = re.findall(DOSAGE_PATTERN, full_text)

        # Detect if this line matches a standard pharmaceutical section heading
        heading_info = self._detect_section_heading(full_text)

        # Detect warnings
        is_warning = False
        warning_keywords = ["تحذير", "احتياط", "خطر", "موانع الاستعمال", "warning", "caution", "contraindication", "danger"]
        for wk in warning_keywords:
            if wk in full_text.lower():
                is_warning = True
                break

        return {
            "text": full_text,
            "tokens": sorted_tokens,
            "bbox": (min_x, min_y, max_x - min_x, max_y - min_y),
            "is_arabic": line_is_arabic,
            "avg_confidence": avg_conf,
            "has_low_confidence": has_low_conf,
            "dosages": dosages,
            "heading": heading_info,
            "is_warning": is_warning
        }

    def _detect_section_heading(self, text: str) -> dict | None:
        """
        Matches a line of text against known pharmaceutical section headers.
        """
        clean_text = text.strip()
        if len(clean_text) > 80:
            return None

        clean_lower = clean_text.lower()
        for sec in PHARMA_SECTIONS:
            # Check Arabic keywords
            for kw in sec["keywords_ar"]:
                if kw in clean_text:
                    return {"id": sec["id"], "title": sec["ar"], "level": 1}
            # Check English keywords
            for kw in sec["keywords_en"]:
                if kw in clean_lower:
                    return {"id": sec["id"], "title": sec["en"], "level": 1}

        # Check generic heading patterns (e.g., numbered headings like "1. Name of the medicinal product")
        numbered_pattern = r"^(\d+[\.\-\)]\s*[\w\s]{3,40})$"
        if re.match(numbered_pattern, clean_text):
            return {"id": "numbered_heading", "title": clean_text, "level": 2}

        return None

    def analyze(self, tokens: list[dict]) -> dict[str, Any]:
        """
        Executes full layout analysis:
        1. Detects columns (1, 2, or 3).
        2. Determines overall and per-column language direction.
        3. Sorts columns in proper reading order:
           - In Arabic RTL: Rightmost column is read first!
           - In English LTR: Leftmost column is read first!
        4. Reconstructs lines, paragraphs, headings, warnings, tables, and dosages.
        5. Returns structured document tree.
        """
        if not tokens:
            return {
                "columns_count": 1,
                "column_boundaries": [(0, self.page_width)],
                "columns": [],
                "ordered_text": "",
                "sections": [],
                "low_confidence_count": 0,
                "dosage_count": 0
            }

        # Determine overall document language
        sample_text = " ".join(t["text"] for t in tokens[:100])
        doc_is_arabic = self.is_arabic_text(sample_text)

        # Detect physical column gutters (left to right)
        physical_columns = self.detect_columns(tokens)
        col_count = len(physical_columns)

        # Group tokens into physical columns
        tokens_by_col = self.assign_tokens_to_columns(tokens, physical_columns)

        # Sort columns according to reading order:
        # If document is Arabic RTL, right-to-left: physical index -1 (right) -> index 0 (left)
        # If document is English LTR, left-to-right: physical index 0 (left) -> index -1 (right)
        column_indices = list(range(col_count))
        if doc_is_arabic:
            reading_order_indices = list(reversed(column_indices))
        else:
            reading_order_indices = column_indices

        structured_columns = []
        ordered_text_blocks = []
        all_sections = []
        total_low_conf = 0
        total_dosages = 0

        for logical_idx, col_idx in enumerate(reading_order_indices):
            col_tokens = tokens_by_col[col_idx]
            col_bounds = physical_columns[col_idx]

            col_sample_text = " ".join(t["text"] for t in col_tokens[:50])
            col_is_arabic = self.is_arabic_text(col_sample_text) if col_sample_text else doc_is_arabic

            lines = self.group_tokens_into_lines(col_tokens, col_is_arabic)

            # Build lines into text
            col_text_lines = []
            col_html_lines = []

            for line in lines:
                line_text = line["text"]
                col_text_lines.append(line_text)

                if line["has_low_confidence"]:
                    total_low_conf += sum(1 for t in line["tokens"] if t.get("is_low_confidence", False))

                if line["dosages"]:
                    total_dosages += len(line["dosages"])

                if line["heading"]:
                    all_sections.append({
                        "heading": line["heading"]["title"],
                        "line": line_text,
                        "column": logical_idx + 1
                    })
                    col_html_lines.append(f"<h3 style='color:#1a56db; margin-top:12px; margin-bottom:4px;'>{line_text}</h3>")
                elif line["is_warning"]:
                    col_html_lines.append(f"<div style='background-color:#fef3c7; border-right:4px solid #f59e0b; padding:4px 8px; margin:4px 0;'><strong>⚠️ {line_text}</strong></div>")
                else:
                    # Highlight words with low confidence with subtle amber span
                    formatted_words = []
                    for t in line["tokens"]:
                        w = t["text"]
                        if t.get("is_low_confidence", False):
                            formatted_words.append(f"<span style='background-color:#fef08a; border-bottom:1px dotted #ca8a04;' title='دقة غير مؤكدة: {t['confidence']:.0f}%'>{w}</span>")
                        else:
                            formatted_words.append(w)
                    direction = "rtl" if line["is_arabic"] else "ltr"
                    col_html_lines.append(f"<p dir='{direction}' style='margin:2px 0;'>{' '.join(formatted_words)}</p>")

            col_full_text = "\n".join(col_text_lines)
            col_html = "\n".join(col_html_lines)
            ordered_text_blocks.append(col_full_text)

            structured_columns.append({
                "logical_index": logical_idx + 1,
                "physical_index": col_idx,
                "bounds": col_bounds,
                "is_arabic": col_is_arabic,
                "lines": lines,
                "plain_text": col_full_text,
                "html": col_html,
                "token_count": len(col_tokens)
            })

        unified_plain_text = "\n\n=== فاصل الأعمدة ===\n\n".join(ordered_text_blocks)

        return {
            "columns_count": col_count,
            "is_arabic": doc_is_arabic,
            "column_boundaries": physical_columns,
            "columns": structured_columns,
            "ordered_text": unified_plain_text,
            "sections": all_sections,
            "low_confidence_count": total_low_conf,
            "dosage_count": total_dosages
        }
