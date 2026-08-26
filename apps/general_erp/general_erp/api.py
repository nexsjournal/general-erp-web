# -*- coding: utf-8 -*-
# general_erp 对外接口（Jinja 打印模板 / 前端可调用）
import frappe

_CN_DIGITS = "零壹贰叁肆伍陆柒捌玖"
_CN_UNITS = ("", "拾", "佰", "仟")
_CN_GROUPS = ("", "万", "亿", "万亿")


def _section_to_cn(value):
	"""1..9999 → 中文大写（不含万/亿单位）"""
	parts = []
	for i in range(3, -1, -1):
		digit = (value // 10**i) % 10
		if digit == 0:
			if parts and parts[-1] != "零":
				parts.append("零")
		else:
			parts.append(_CN_DIGITS[digit] + _CN_UNITS[i])
	return "".join(parts)


@frappe.whitelist()
def money_in_words_cn(amount, currency="CNY"):
	"""金额转中文大写，如 2500 → 人民币贰仟伍佰元整"""
	try:
		amount = round(float(amount or 0), 2)
	except (TypeError, ValueError):
		amount = 0.0

	negative = amount < 0
	amount = abs(amount)
	cents = int(round(amount * 100))
	integer = cents // 100
	jiao = (cents // 10) % 10
	fen = cents % 10

	if integer == 0:
		number_text = "零"
	else:
		groups = []
		number = integer
		while number > 0:
			groups.append(number % 10000)
			number //= 10000
		parts = []
		for index in range(len(groups) - 1, -1, -1):
			group = groups[index]
			if group == 0:
				if parts and not parts[-1].endswith("零"):
					parts.append("零")
			else:
				if parts and group < 1000 and not parts[-1].endswith("零"):
					parts.append("零")
				parts.append(_section_to_cn(group) + _CN_GROUPS[index])
		number_text = "".join(parts)
	if len(number_text) > 1 and number_text.endswith("零"):
		number_text = number_text[:-1]

	text = number_text + "元"
	if jiao == 0 and fen == 0:
		text += "整"
	else:
		if jiao > 0:
			text += _CN_DIGITS[jiao] + "角"
		elif integer > 0 and fen > 0:
			text += "零"
		if fen > 0:
			text += _CN_DIGITS[fen] + "分"

	if currency == "CNY":
		text = "人民币" + text
	else:
		text = f"{currency} " + text
	return "负" + text if negative else text
