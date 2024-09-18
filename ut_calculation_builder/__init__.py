import pandas as pd
from ut_calculation_builder.Utilities.logger import logger
from ut_calculation_builder.Utilities.common_utils import CommonUtils
from ut_calculation_builder.constants import ExpressionConstant
from ut_calculation_builder.exceptions import ParenthesisError, ExpressionValidationError
from ut_calculation_builder.Utilities.rules_util import RuleExpressionUtil
from ut_calculation_builder.schemas import WidgetSaveRequest


class CalculationBuilderUtility:
    def __init__(self):
        self.rules_utils = RuleExpressionUtil()
        self.common_utils = CommonUtils()

    def validate_chart_expressions(self, request_data: WidgetSaveRequest):
        try:
            if formula_info := request_data.widget_data.get("cData", {}).get("chartOptions", {}).get("formulaInfo", {}):
                chart_expressions = self.rules_utils.get_pd_eval_expression(formula_info)
                pattern = self.common_utils.get_pattern_string(request_data.project_id)
                replaced_chart_expressions = [pattern.sub("0", data) for data in chart_expressions]
                for expression in replaced_chart_expressions:
                    _, expression_str = expression.split("=", 1)
                    validation = self.validate_balanced_parenthesis(expression_str)
                    if validation in ["Unbalanced", None]:
                        raise ParenthesisError
                    pd.eval(
                        expression_str,
                        engine="python",
                        parser="pandas",
                        local_dict=ExpressionConstant.expression_mapping,
                    )
                request_data.widget_data.get("cData", {}).get("chartOptions", {}).update(
                    {"chart_expressions": chart_expressions}
                )
            else:
                request_data.widget_data.get("cData", {}).get("chartOptions", {}).update({"chart_expressions": []})
        except ParenthesisError:
            raise ParenthesisError
        except (pd.errors.ParserError, ValueError) as e:
            raise ExpressionValidationError(e)
        except Exception as e:
            logger.exception(e)

    @staticmethod
    def validate_balanced_parenthesis(expression_str):
        response = None
        try:
            open_list = ["[", "{", "("]
            close_list = ["]", "}", ")"]
            stack = []
            for i in expression_str:
                if i in open_list:
                    stack.append(i)
                elif i in close_list:
                    pos = close_list.index(i)
                    if (len(stack) > 0) and (open_list[pos] == stack[len(stack) - 1]):
                        stack.pop()
                    else:
                        response = "Unbalanced"
                        return response
            response = "Balanced" if len(stack) == 0 else "Unbalanced"

        except Exception as e:
            logger.error(f"Error occurred in balance parenthesis due to {str(e)} ")
        return response
