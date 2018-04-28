# -*- coding: utf8 -*-

"""
設定情報を扱う
"""

import re
import os.path


class SubtitleConfig:
    """
    設定を保持するクラス
    """

    def __init__(self):
        self.config = {}
        self.config['font_name'] = os.path.join(os.path.dirname(__file__), 'SourceHanSansJP-Regular.otf')

    def parse(self, filepath):
        """
        ファイルパスを指定して設定を読込
        """

        with open(filepath, 'r') as f:

            bracket = False # 今カッコ内かどうか
            bracket_name = None
            bracket_value_list = None
            for line in f:

                # 空行は飛ばす
                if line.strip() == '':
                    continue

                # カッコの外
                if bracket is False:

                    # イコールで分割
                    v = line.split('=')
                    name = v[0].strip()
                    value = v[1].strip()

                    # カッコではない時
                    if value != '{':

                        # 数値はintに変換
                        if re.search(r'^\d+$', value) is not None:
                            self.config[name] = int(value)
                        elif re.search(r'^\d+\.\d+$', value) is not None:
                            self.config[name] = float(value)
                        elif re.search(r'^True$', value) is not None:
                            self.config[name] = True
                        elif re.search(r'^False$', value) is not None:
                            self.config[name] = False
                        else:
                            self.config[name] = value

                    # カッコ内に侵入
                    else:
                        bracket_name = name
                        bracket_value_list = []
                        bracket = True

                # カッコ内の処理
                elif bracket is True:

                    if line.strip() == '}':
                        self.config[bracket_name] = bracket_value_list
                        bracket = False

                    else:
                        bracket_value_list.append(line.strip())

    def __getattr__(self, name):
        """
        オブジェクトの属性を取得
        obj.key で設定辞書にアクセスできるようにする
        """

        if name in self.config:
            return self.config[name]
        else:
            raise AttributeError('Config not found: "{}"'.format(name))

    class InvalidValueException(Exception):
        pass