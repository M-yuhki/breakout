# breakout
趣味で作ってみたブロック崩しゲームです

# ディレクトリ構成
├─ breakout.py 実行用ファイル  
├─ data 実行に必要なデータを格納したディレクトリ   
│ ├─ ~.png ゲーム中で描画するアイテムのデータ  
│ ├─ ~.wav ゲーム中で鳴らすサウンドデータ  
│ └─ ~.csv ステージデータ   
└─ ranking.txt ゲームの記録を保存しておくtxtファイル（準備中）  

# 実行方法  
※実行にはpygameなど幾つかのモジュールの導入が必要です  
 別途導入をお願いします  
`python pygame.py`  
上記の通り実行することでウィンドウが設定され、以下のようなTOP画面が表示されます  
![TOP画面](https://github.com/M-yuhki/breakout/blob/image/game_home.png)

## start
ゲームを開始するボタンです  

## option
optionボタンでは、ステージの選択と、プレイ人数の選択ができます  
rankingボタンでは、ランキングを確認できます  

# ステージデータについて
dataディレクトリ内にcsvファイルを作るとステージを自作できます  
ブロックを設置したいところには1,それ以外には0を記述してください  
※あまりに範囲が大きいと適切に実行できない可能性があります。10×10程度のサイズを推奨します  
作成したファイルをbreakout.py内のRead関数内に明示することで選択可能になります  


# 参考サイト
http://lumenbolk.com : ゲーム本体の作成時に参考  
http://taira-komori.jpn.org/freesound.html : SEを使用
