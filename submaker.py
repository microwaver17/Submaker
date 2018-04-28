# -*- coding: utf8 -*-

'''
字幕作成ソフトウェア
'''

from pprint import pformat
from PIL import Image
import argparse
import os.path
import sys
import os
import shutil
import logging

import config_util
import painter


class Submaker:

    config = None
    config_path = None      # 設定ファイル
    background_path = None  # 試し刷りの背景ファイル
    output_path = None      # 出力ディレクトリ
    trial_path = None       # 試し刷りの出力ファイル

    CONFIG_FNAME = 'config.txt'
    BACKGROUND_FNAME = 'background'
    OUTPUT_DIRNAME = 'output'
    TRIAL_FNAME = 'trial.png'

    def main(self):
        print(__file__)
        # コマンドライン引数
        # usage: submaker.py [-h] [--trial] working_directory
        ap = argparse.ArgumentParser()
        ap.add_argument('working_directory',
                        help='working directory contains "config.txt" (optionally "background.jpg/png" for trial)')
        ap.add_argument('-t', '--trial', action='store_true', help='trial print (tameshizuri)')
        ap.add_argument('-v', '--verbose', action='store_true', help='show debug message')
        args = ap.parse_args()

        # デバッグメッセージを表示するかの設定
        if args.verbose:
            logging.basicConfig(level=logging.DEBUG)

        # 各種ファイルパスの存在確認と設定
        self.prepare_filepath(args.working_directory, args.trial)

        # 設定ファイルの読み込み
        self.config = config_util.SubtitleConfig()
        self.config.parse(self.config_path)
        logging.debug('[Configurations]\n' + pformat(self.config.config))

        # 試し刷りの生成
        if args.trial is True:
            print('generate trial: ' + self.trial_path)
            canvas = self.paint_procedure(self.config.scripts[0], self.background_path)
            canvas.save(self.trial_path)

        # 本番の画像を生成
        else:
            for i, script in enumerate(self.config.scripts):

                # ファイル名の作成と好ましくない文字の削除
                fname = '{:03d}_{}.png'.format(i, script)
                fname = fname.replace('\n', '(NL)')
                for ch in '/><?:"\\*|;~^}]{[`&%$#\'! 　':
                    fname = fname.replace(ch, '_')
                print('generate [{:3}/{:3}]: {}'.format(i + 1, len(self.config.scripts), fname))

                # 画像を生成
                canvas = self.paint_procedure(script)
                canvas.save(os.path.join(self.output_path, fname))

    def prepare_filepath(self, dirpath, is_trial):
        """
        ディレクトリにちゃんとファイルが有るか
        各種ファイルのパスをインスタンス変数に設定
        出力フォルダを用意
        dirpath: ワーキングディレクトリ
        """

        # ワーキングディレクトリが有るか
        if os.path.exists(dirpath) is False:
            sys.exit('指定のディレクトリが存在しません')

        # 設定ファイルが有るか
        self.config_path = os.path.join(dirpath, self.CONFIG_FNAME)
        if os.path.exists(self.config_path) is False:
            sys.exit('設定ファイルが存在しません: ' + self.CONFIG_FNAME)

        # 試し刷りモード
        if is_trial is True:

            # 背景ファイルが有るか（jpg or png）
            self.background_path = os.path.join(dirpath, self.BACKGROUND_FNAME + '.jpg')
            if os.path.exists(self.background_path) is False:

                self.background_path = os.path.join(dirpath, self.BACKGROUND_FNAME + '.png')
                if os.path.exists(self.background_path) is False:

                  sys.exit('背景ファイルが存在しません: ' + self.BACKGROUND_FNAME + '.jpg/png')

            # 試し刷りの出力パス
            self.trial_path = os.path.join(dirpath, self.TRIAL_FNAME)

        # 本番モード
        if is_trial is False:

            # 出力フォルダを空の状態にする
            self.output_path = os.path.join(dirpath, self.OUTPUT_DIRNAME)
            shutil.rmtree(self.output_path, ignore_errors=True)
            os.mkdir(self.output_path)

    def paint_procedure(self, text, background_path=None, bounding_box=False):
        """
        画像の生成手順
        text: 描画する文字列
        return: できたPIL.Image
        """

        resolution = (self.config.screen_resolution_x, self.config.screen_resolution_y)
        canvas = Image.new('RGBA', resolution, (255, 255, 255, 0))

        # 試し刷り用背景を描画
        if background_path is not None:
            ip = painter.ImagePainter(self.config, canvas, background_path)
            ip.paint()

        # シャドウブラーを表示
        tbp = painter.TextBlurPainter(self.config, canvas, text)
        tbp.paint()

        # 文字のフチを描画
        top = painter.TextOutlinePainter(self.config, canvas, text)
        top.paint()

        # 文字を描画
        tp = painter.TextPainter(self.config, canvas, text)
        tp.paint()

        return canvas


if __name__ == '__main__':

        submaker = Submaker()
        submaker.main()