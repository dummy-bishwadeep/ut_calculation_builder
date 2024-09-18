import re

import numpy as np
import pandas as pd

from ut_calculation_builder import ExpressionConstant
from ut_calculation_builder.Utilities.logger import logger


class RuleExpressionUtil:
    def __init__(self):
        pass

    def get_pd_eval_expression(self, formula_info):
        try:
            if not formula_info:
                return []
            code_id = formula_info.get("code_id", "")
            expression_list = code_id.split(";")
            expression_list = [data.strip() for data in expression_list if data]
            expressions = self.get_formed_expression(expression_list)
            return expressions
        except Exception as e:
            logger.exception(e)

    def get_formed_expression(self, expression_list):
        try:
            expression_list = self.update_sum_expressions(expression_list)
            expression_list = self.update_avg_expressions(expression_list)
            expression_list = [expression_str.replace("$", "dollar") for expression_str in expression_list]
            return expression_list
        except Exception as e:
            logger.exception(e)

    def update_sum_expressions(self, expression_list):
        try:
            return [re.sub(r"sum\((.*?)\)", self.replace_sum, data) for data in expression_list]
        except Exception as e:
            logger.exception(e)

    def update_avg_expressions(self, expression_list):
        try:
            return [re.sub(r"avg\((.*?)\)", self.replace_avg, data) for data in expression_list]
        except Exception as e:
            logger.exception(e)

    @staticmethod
    def replace_sum(match):
        return match.group(1).replace(",", "+")

    @staticmethod
    def replace_avg(match):
        return f"avg([{match.group(1)}],axis=0)"

    @staticmethod
    def update_df_on_expression(df, metadata):
        try:
            if not metadata.chart_expressions:
                return df
            hierarchy = "$".join(metadata.ui_filters.get("hierarchy", {}).values())
            ui_filter_hierarchy = []
            replace_dynamic_tag = {}
            if (
                (metadata.hierarchy or metadata.selected_hierarchy) + metadata.static_selected_tags
                and metadata.is_dynamic
                and hierarchy
            ):
                for data in metadata.hierarchy or metadata.selected_hierarchy:
                    replace_dynamic_tag[data] = f"{hierarchy}${data}"
                    ui_filter_hierarchy.append(f"{hierarchy}${data}")
            copied_df = df.copy()
            df_column_dict = {}
            for data in (
                (metadata.hierarchy or metadata.selected_hierarchy)
                + metadata.static_selected_tags
                + ui_filter_hierarchy
            ):
                if data not in copied_df.columns:
                    copied_df[data] = 0
            copied_df.rename(columns=lambda x: x.replace("$", "dollar"), inplace=True)
            for column in copied_df.columns:
                df_column_dict[column] = copied_df[column].copy()
                if pd.isna(df_column_dict[column].values).any():
                    # Replace NaN values with 0
                    df_column_dict[column].fillna(0, inplace=True)
            local_dict = {}
            local_dict.update(ExpressionConstant.expression_mapping)
            local_dict.update(df_column_dict)
            for expression in metadata.chart_expressions:
                identifier, expression_str = expression.split("=", 1)
                if metadata.is_dynamic and hierarchy:
                    for key, value in replace_dynamic_tag.items():
                        expression_str = re.sub(rf"(?<!dollar){key}", value, expression_str)
                        expression_str = expression_str.replace("$", "dollar")
                df[identifier] = pd.eval(expression_str, engine="python", parser="pandas", local_dict=local_dict).copy()
                df[identifier] = df[identifier].replace({None: np.nan})
                metadata.chart_expressions_identifiers.append(identifier)
            return df
        except Exception as e:
            logger.exception(e)
            return df
