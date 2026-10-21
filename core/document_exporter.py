"""
PharmaLeaf AI - Document Exporter
Exports extracted pharmaceutical leaflets to DOCX, PDF, HTML, TXT,
and manages rich clipboard copying with full Arabic RTL and English LTR support.
"""
import os
from typing import Any
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls


class DocumentExporter:
    @staticmethod
    def export_docx(
        doc_data: dict[str, Any],
        output_path: str,
        page_size: str = "A4",
        margins_in_inches: float = 0.75,
        font_name: str = "Arial"
    ) -> bool:
        """
        Exports structured document to Microsoft Word DOCX with genuine RTL support,
        styled headings, warning callouts, and clean typography.
        """
        doc = docx.Document()

        # Set page size and margins
        section = doc.sections[0]
        if page_size.upper() == "A4":
            section.page_width = Inches(8.27)
            section.page_height = Inches(11.69)
        elif page_size.upper() == "A5":
            section.page_width = Inches(5.83)
            section.page_height = Inches(8.27)
        elif page_size.upper() == "LETTER":
            section.page_width = Inches(8.5)
            section.page_height = Inches(11.0)

        section.top_margin = Inches(margins_in_inches)
        section.bottom_margin = Inches(margins_in_inches)
        section.left_margin = Inches(margins_in_inches)
        section.right_margin = Inches(margins_in_inches)

        is_doc_arabic = doc_data.get("is_arabic", True)

        # Iterate over columns in reading order
        columns = doc_data.get("columns", [])
        for col_idx, col in enumerate(columns):
            if len(columns) > 1:
                # Column header banner
                col_heading = doc.add_paragraph()
                col_run = col_heading.add_run(f"--- العمود {col['logical_index']} ---" if is_doc_arabic else f"--- Column {col['logical_index']} ---")
                col_run.font.name = font_name
                col_run.font.size = Pt(10)
                col_run.font.color.rgb = RGBColor(128, 128, 128)
                col_run.italic = True
                col_heading.alignment = WD_ALIGN_PARAGRAPH.RIGHT if is_doc_arabic else WD_ALIGN_PARAGRAPH.LEFT

            for line in col.get("lines", []):
                text = line["text"].strip()
                if not text:
                    continue

                p = doc.add_paragraph()
                line_arabic = line.get("is_arabic", is_doc_arabic)

                # Enable RTL on paragraph level in OpenXML if Arabic
                if line_arabic:
                    pPr = p._p.get_or_add_pPr()
                    pPr.append(parse_xml(f'<w:bidi {nsdecls("w")}/>'))
                    p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
                else:
                    p.alignment = WD_ALIGN_PARAGRAPH.LEFT

                if line.get("heading"):
                    run = p.add_run(text)
                    run.font.name = font_name
                    run.font.size = Pt(13)
                    run.font.bold = True
                    run.font.color.rgb = RGBColor(26, 86, 219) # Pharma Blue
                    p.paragraph_format.space_before = Pt(8)
                    p.paragraph_format.space_after = Pt(3)
                elif line.get("is_warning"):
                    # Warning Callout
                    run = p.add_run("⚠️ " + text)
                    run.font.name = font_name
                    run.font.size = Pt(10.5)
                    run.font.bold = True
                    run.font.color.rgb = RGBColor(180, 83, 9) # Amber
                    p.paragraph_format.space_before = Pt(4)
                    p.paragraph_format.space_after = Pt(4)
                else:
                    # Regular text line with dosage highlighting
                    p.paragraph_format.space_before = Pt(1)
                    p.paragraph_format.space_after = Pt(2)
                    p.paragraph_format.line_spacing = 1.15

                    for t in line.get("tokens", []):
                        run = p.add_run(t["text"] + " ")
                        run.font.name = font_name
                        run.font.size = Pt(10)

                        if t.get("is_low_confidence", False):
                            # Mark low confidence in subtle gray/yellow
                            run.font.color.rgb = RGBColor(160, 110, 0)

        doc.save(output_path)
        return True

    @staticmethod
    def export_html(
        doc_data: dict[str, Any],
        output_path: str,
        title: str = "PharmaLeaf AI - النشرة الدوائية المستخرجة"
    ) -> bool:
        """
        Exports clean, modern, self-contained HTML with responsive columns,
        print styles, and RTL support.
        """
        is_doc_arabic = doc_data.get("is_arabic", True)
        direction = "rtl" if is_doc_arabic else "ltr"
        align = "right" if is_doc_arabic else "left"

        columns = doc_data.get("columns", [])
        col_count = max(1, len(columns))

        html_parts = [
            "<!DOCTYPE html>",
            f"<html lang='{'ar' if is_doc_arabic else 'en'}' dir='{direction}'>",
            "<head>",
            "<meta charset='utf-8'>",
            "<meta name='viewport' content='width=device-width, initial-scale=1.0'>",
            f"<title>{title}</title>",
            "<style>",
            ":root { --primary: #1a56db; --bg: #f8fafc; --text: #0f172a; --card: #ffffff; }",
            "body { font-family: 'Segoe UI', Tahoma, Arial, sans-serif; background: var(--bg); color: var(--text); margin: 0; padding: 24px; line-height: 1.6; }",
            ".container { max-width: 1100px; margin: 0 auto; background: var(--card); padding: 32px; border-radius: 12px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); }",
            ".header { border-bottom: 2px solid #e2e8f0; padding-bottom: 16px; margin-bottom: 24px; display: flex; justify-content: space-between; align-items: center; }",
            ".header h1 { margin: 0; color: var(--primary); font-size: 22px; }",
            ".header .badge { background: #e0f2fe; color: #0369a1; padding: 4px 12px; border-radius: 9999px; font-size: 13px; font-weight: 600; }",
            f".columns-grid {{ display: grid; grid-template-columns: repeat({col_count}, 1fr); gap: 24px; }}",
            ".column { background: #fdfdfd; padding: 16px; border: 1px solid #f1f5f9; border-radius: 8px; }",
            ".column-title { font-size: 13px; font-weight: bold; color: #64748b; margin-bottom: 12px; border-bottom: 1px solid #e2e8f0; padding-bottom: 4px; }",
            "h3 { color: var(--primary); margin-top: 14px; margin-bottom: 6px; font-size: 16px; }",
            "p { margin: 4px 0; font-size: 14px; text-align: justify; }",
            ".warning-box { background: #fef3c7; border-right: 4px solid #f59e0b; padding: 8px 12px; margin: 8px 0; border-radius: 4px; font-weight: bold; }",
            ".unclear { background-color: #fef08a; border-bottom: 1px dotted #ca8a04; border-radius: 2px; padding: 0 2px; }",
            "@media print { body { background: white; padding: 0; } .container { box-shadow: none; padding: 0; max-width: 100%; } .no-print { display: none; } }",
            "</style>",
            "</head>",
            "<body>",
            "<div class='container'>",
            "<div class='header'>",
            f"<h1>{title}</h1>",
            f"<span class='badge'>{col_count} أعمدة مكتشفة | PharmaLeaf AI</span>" if is_doc_arabic else f"<span class='badge'>{col_count} Columns | PharmaLeaf AI</span>",
            "</div>",
            "<div class='columns-grid'>"
        ]

        for col in columns:
            col_title = f"العمود {col['logical_index']}" if is_doc_arabic else f"Column {col['logical_index']}"
            html_parts.append(f"<div class='column'>")
            html_parts.append(f"<div class='column-title'>{col_title}</div>")
            html_parts.append(col.get("html", ""))
            html_parts.append("</div>")

        html_parts.extend([
            "</div>",
            "<div class='footer' style='margin-top:32px; padding-top:16px; border-top:1px solid #e2e8f0; font-size:12px; color:#94a3b8; text-align:center;'>",
            "تم الاستخراج والمعالجة بواسطة PharmaLeaf AI — دقة وموثوقية النشرات الطبية",
            "</div>",
            "</div>",
            "</body>",
            "</html>"
        ])

        with open(output_path, "w", encoding="utf-8") as f:
            f.write("\n".join(html_parts))

        return True

    @staticmethod
    def export_txt(doc_data: dict[str, Any], output_path: str, separate_columns: bool = True) -> bool:
        """
        Exports plain text file preserving reading order and column separators.
        """
        text = doc_data.get("ordered_text", "")
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(text)
        return True

    @staticmethod
    def get_column_plain_text(doc_data: dict[str, Any], column_idx: int) -> str:
        """
        Retrieves plain text for a single column (0-indexed).
        """
        columns = doc_data.get("columns", [])
        if 0 <= column_idx < len(columns):
            return columns[column_idx].get("plain_text", "")
        return ""

    @staticmethod
    def get_column_html(doc_data: dict[str, Any], column_idx: int) -> str:
        """
        Retrieves rich HTML for a single column (0-indexed).
        """
        columns = doc_data.get("columns", [])
        if 0 <= column_idx < len(columns):
            return columns[column_idx].get("html", "")
        return ""
