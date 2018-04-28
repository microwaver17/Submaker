# -*- coding: utf8 -*-

"""
画像描画モジュール
"""

from PIL import ImageDraw, ImageFont, Image, ImageFilter
import math


class AbstractPainter:

    def __init__(self, config, canvas):
        """
        コンストラクタ
            config: SubtitleConfig
        子クラスでは
            super().__init__(config)
        で必ず呼んで
        """

        self.config = config
        self.canvas = canvas

    def paint(self):
        """
        描画する
        新しいレイヤーを作って、元の画像に合成する
        """

        resolution = (
                self.config.screen_resolution_x,
                self.config.screen_resolution_y
                )
        new_layer = Image.new('RGBA',resolution , (255, 255, 255, 0))

        new_layer = self._paint(new_layer)

        self.canvas.alpha_composite(new_layer)

    def _paint(self, new_layer):
        """
        新しいレイヤーに描画する
        new_layer: 描画対象
        return: 描画したもの
        """
        pass


class TextPainter(AbstractPainter):
    """
    文字を描画する
    """

    font = None
    position = None
    font_color = None

    def __init__(self, config, canvas, text):
        """
        コンストラクタ
        config: SubtitleConfig
        canvas: PIL.Image
        text: str
        """

        super().__init__(config, canvas)
        self.text = text
        self.font = ImageFont.truetype(self.config.font_name, self.config.font_size)

        self.inflate_config()

    def inflate_config(self):
        """
        Configをオブジェクトに展開する
        """

        # 文字が描画されるサイズを取得
        drawer = ImageDraw.Draw(self.canvas)
        bounding_box = drawer.multiline_textsize(self.text, font=self.font)

        self.position = [0, 0]

        # ---- 水平方向 ----
        # 水平左寄せ
        if self.config.position_horizontal_align == 'left':

            self.position[0] = self.config.position_lefttop_x

        # 真ん中寄せ
        elif self.config.position_horizontal_align == 'center':

            width = self.config.position_rightbottom_x - self.config.position_lefttop_x
            self.position[0] = self.config.position_lefttop_x + (width / 2) - (bounding_box[0] / 2)

        # 右寄せ
        elif self.config.position_horizontal_align == 'right':

            self.position[0] = self.config.position_rightbottom_x - bounding_box[0]

        else:
            raise self.config.InvalidValueException(
                'horizontal align "{}" is invalid'.format(self.config.position_align))

        # ---- 垂直方向 ----
        # 水平左寄せ
        if self.config.position_vertical_align == 'top':

            self.position[1] = self.config.position_lefttop_y

        # 真ん中寄せ
        elif self.config.position_vertical_align == 'middle':

            height = self.config.position_rightbottom_y - self.config.position_lefttop_y
            self.position[1] = self.config.position_lefttop_y + (height / 2) - (bounding_box[1] / 2)

        # 右寄せ
        elif self.config.position_vertical_align == 'bottom':

            self.position[1] = self.config.position_rightbottom_y - bounding_box[1]

        else:
            raise self.config.InvalidValueException(
                'vertical align "{}" is invalid'.format(self.config.position_align))

        self.font_color = (
                self.config.font_color_r,
                self.config.font_color_g,
                self.config.font_color_b
                )

    def _paint(self, new_layer):
        """
        描画する
        """

        drawer = ImageDraw.Draw(new_layer)
        drawer.text(self.position, self.text, font=self.font, fill=self.font_color)

        return new_layer


class TextOutlinePainter(TextPainter):
    """
    文字のフチを描画
    """

    outline_color = None
    outline_size = None

    def inflate_config(self):
        """
        Configをオブジェクトに展開する
        """

        super().inflate_config()

        self.outline_color = (
                self.config.outline_color_r,
                self.config.outline_color_g,
                self.config.outline_color_b
                )
        self.outline_size = self.config.outline_size

    def _paint(self, new_layer):
        """
        描画する
        """

        drawer = ImageDraw.Draw(new_layer)

        for i in range(64):
            x = math.cos(2.0*3.14159 * i / 64) * self.outline_size
            y = math.sin(2.0*3.14159 * i / 64) * self.outline_size
            shifted = (self.position[0] + x, self.position[1] + y)
            drawer.text(shifted, self.text, font=self.font, fill=self.outline_color)

        return new_layer


class TextBlurPainter(TextPainter):
    """
    文字のシャドウブラーを描画
    """

    blur_color = None
    blur_size = None
    blur_size = None

    def inflate_config(self):
        """
        Configをオブジェクトに展開する
        """

        super().inflate_config()

        self.blur_color = (
                self.config.blur_color_r,
                self.config.blur_color_g,
                self.config.blur_color_b
                )
        self.blur_size = self.config.blur_size

    def _paint(self, new_layer):
        """
        描画する
        """

        drawer = ImageDraw.Draw(new_layer)
        for i in range(64):
            x = math.cos(2.0*3.14159 * i / 64) * self.blur_size
            y = math.sin(2.0*3.14159 * i / 64) * self.blur_size
            shifted = (self.position[0] + x, self.position[1] + y)
            drawer.text(shifted, self.text, font=self.font, fill=self.blur_color)

        new_layer = new_layer.filter(ImageFilter.GaussianBlur(self.blur_size))

        return new_layer


class ImagePainter(AbstractPainter):
    """
    画像を描画
    """

    def __init__(self, config, canvas, filepath):
        '''
        コンストラクタ
        filepath: 画像のファイルパスを取る
        canvas: 描画する対象
        '''

        super().__init__(config, canvas)
        self.filepath = filepath

    def _paint(self, new_layer):
        """
        画像を描画
        """

        image = Image.open(self.filepath)
        new_layer.paste(image)

        return new_layer