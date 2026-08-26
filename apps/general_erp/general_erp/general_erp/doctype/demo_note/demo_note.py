import frappe

from frappe.model.document import Document


class DemoNote(Document):
    """示例自定义单据：验证 general_erp 二开链路。确认无误后可删除本目录。"""

    def on_submit(self):
        # 单据提交钩子示例
        pass
