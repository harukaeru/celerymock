name: inverse
layout: true
class: center, middle, inverse
---

# Celeryよくわかんなかったので実装した

---
.left[
## アジェンダ

1. Celeryの概要
2. Consumer + Producer パターンの概要
3. キューについて
4. 排他制御の実装
5. Queueの実装
6. 実装したものを使ってCeleryもどきを構築する
7. 動かしてみる
8. |Celeryもどきを実装した結果| ┗(☋｀ )┓三
]

---
.left[
## 1. Celeryの概要

( ^o^) Celeryとは

- 非同期処理するやつ
- ジョブキュー(ブローカー)にメッセージを投げて、ワーカーがそのジョブキューからメッセージを読んでタスクを実行する
- 一般的なProducer + Consumerパターンをリッチにしたもの

( ˘⊖˘) 。o(なるほどな！！わかりやすい！！！)

]

---
.left[

だいたいこんな感じ

![](django_celery_architecture.png)

]

---

### 2. Consumer + Producer パターンの概要

.left[

たとえばJSで次のようなコードがあったとする

```js
const add = (a, b) => console.log(a + b)

add(2, 3)
```

処理したい関数がものすっごい時間かかる関数だった場合、同期処理にすると時間がかかってしまう。

]

---

.left[

処理してよって命令だけ投げて、処理するのは別でやりたい。

Main
```js
const message = ['add', [2, 3]]

queue.enqueue(message)
```

Worker
```js
message = queue.dequeue()

const tasks = {
    add: (a, b) => console.log(a + b)
}

tasks[message[0]](...message[1])
```

※疑似コードなので実装しないと動きません。

]

---

.left[

### 実際に動くJS(不完全)

DEMO

]

---

### この実装の問題点

非同期じゃないから無意味(コード長くなっただけ)

---

.left[

### 3. キューについて

- FIFO(最初に入れたものを最初に出す)という構造
- 待ち行列という意味。ラーメン屋の待ち行列と同じ。最初に並んだやつが最初に店に入れる。
- ジョブキューは、ジョブのキュー。redmineのチケットがジョブみたいなもん

```js
queue = [1, 2, 3]
queue.enqueue(5)  // queueは [1, 2, 3, 5]
queue.dequeue()  // -> 1
```

常識だぞ!!

]

---

.left[

### 4. 排他制御

- 同じタイミングでデータにアクセスするためには排他制御が必要!
- ほんとに同時にアクセスしても問題ないようにしたり(Atomicity[原子性])
- 自分がアクセスするときは他のやつらを待たせたりする

]

---

.left[

今回排他制御に使うのはDekker's Algorithm

↓ Javaで書かれた実装
https://www.enseignement.polytechnique.fr/informatique/INF431/X13-2014-2015/TD/INF431-td_3a-1.php

]

---

.left[
```java
class Dekker {
  private int turn;
  private boolean [] flag = new boolean [2];
  public Dekker () {
    flag[0] = false; flag[1] = false; turn = 0; // 各プロセスのフラグを生成
  }

  public void Pmutex(int t) {  // 処理を実行するという宣言を行う
    int other;

    other = 1-t;
    flag[t] = true;  // 俺は実行するぞ俺は!!
    while (flag[other] == true) { // えっお前もやるんかいってとき
      // 相手のターンのときは仕方ないから自分が我慢して待ってあげる
      if (turn == other) {
        flag[t] = false;
        while (turn == other);  // 「まだ終わらんのかよ。さっさとしろよ」ゾーン
        flag[t] = true;  // 俺は実行するぞ俺は!! 誰も入るなや!!
      }
      // 自分のターンのときは当然自分が実行できるはず
      // なので他のやつらが諦めるまで待つ
    }
  }

  public void Vmutex(int t) { // 処理を終えたという宣言を行う
    turn = 1-t;
    flag[t] = false;  // 俗に言う「俺のターンは終了だ」
  }
}
```

]

---

### 使い方

.left[

```python
dekker = Dekker()

dekker.Pmutex(0)  # 排他制御された処理をすることを宣言
doSomething()
dekker.Vmutex(0)  # 排他制御された処理を終えたことを宣言

```

PとかVとかいうのはオランダ語らしい。そういうのすごい嫌
]

---

### デッカーのアルゴリズムの基本原理

.left[

```
処理を実行する前に「絶対自分は実行する」って宣言する。(flagをオンにする)
宣言したあとで、他の誰も何も宣言していなかったら実行する
他の誰かが宣言してたらちょっと待つ
```

```
自分のターンではない場合、
「やっぱ止めます」という意味で「実行はしませんよ」と宣言する(flagをオフにする)

他のプロセスが終わるまで待ち、
そのプロセスが終了したら、再度自分が実行することを宣言する。
```

```
自分のターンの場合、相手が実行を中止してくれるはずなのでそれを待つ
```

```
自分のターンが終了したら、ターンを相手に渡し、実行はしませんよと宣言する(flagをオフにする)
```

見てわかるとおり、デッカーのアルゴリズムはプロセス数2までしか対応していない(拡張すればいけそう)

]

---

### 実際にデッカーのアルゴリズムを体で体験する

DEMO(適当に2人選ぶ)


---

### 今回の実装に適応する

このコード自体はJavaのスレッドに適応するものなので、置き換える

---

### こんな感じ

.left[
mutex.py
```python
def p_mutex(process_id):
    other_process_id = 1 - process_id
    flag_on(process_id)

    while read_flag(other_process_id):
        turn = get_current_turn()
        flag_off(process_id)

        while turn == other_process_id:
            pass
        flag_on(process_id)


def v_mutex(process_id):
    other_process_id = 1 - process_id
    give_turn_to(other_process_id)
    flag_off(process_id)
```

Javaのコードにはあったturnやflagを定義してたとこはファイルにして、

ファイルの名前を変数名、ファイルの内容を変数の内容というふうに使ってみた

]

---

### このファイルを変数として使ってる

.left[
```sh
$ ls mutexfiles/
0   1   turn
```

この0とか1は、おのおののプロセスにあとで与えるID

なんでファイルに定義してるかというと、おのおののプロセスからアクセスできる共有資源としたかったから

0には、疑似プロセスIDが0のフラグが入り、1には、疑似プロセスIDが1のフラグが入る
]

---

.left[
```python
def get_current_turn():
    with open(f"mutexfiles/turn", 'r') as f:
        return f.read()


def give_turn_to(next_process_id):
    with open(f"mutexfiles/turn", 'w') as f:
        return f.write(str(next_process_id))


def read_flag(process_id):
    with open(f"mutexfiles/{process_id}", 'r') as f:
        return f.read() == '1'


def flag_on(process_id):
    with open(f"mutexfiles/{process_id}", 'w') as f:
        f.write('1')


def flag_off(process_id):
    with open(f"mutexfiles/{process_id}", 'w') as f:
        f.write('0')
```

中身はファイルを読んだり書いたりしてるだけ
]

---

### 排他制御の実装終了

---

### 5. Queueの実装
.left[
```python
task_funcs = {}

# ConsumerからQueueにデータを入れる　
def enqueue(func_name, *args, **kwargs):
    serialized_data = json.dumps([func_name, args, kwargs])
    filename = str(datetime.datetime.timestamp(datetime.datetime.now()))
    with open(f'database/{filename}', 'w') as f:
        f.write(serialized_data)


# Producerから呼び出して使う
def dequeue(process_id):
    p_mutex(process_id)
    filenames = os.listdir('database')
    if not len(filenames):
        v_mutex(process_id)
        return

    peek_filename = f'database/{filenames[0]}'
    with open(peek_filename, 'r') as f:
        data = json.loads(f.read())
    func_name = data[0]
    task_func = task_funcs[func_name]
    task_func(*data[1], **data[2])
    os.remove(peek_filename)
    v_mutex(process_id)
```
]

---

### いちおう解説
.left[
enqueue
```
json.dumpsで引数の組み合わせ['add', (2, 3), {}]のようなものをJSON化する
filenameはタイムスタンプをもとに生成(本来はたぶんUUIDを使う)
あとでos.listdir関数【シェルのlsとほぼ等価】を使ったときに先頭に来させるため
```

dequeue
```
p_mutexで排他制御処理の実行を宣言
ファイルがあったら一番タイムスタンプが古いものを取得
中のデータをとって、タスクを実行する

v_mutexで排他制御処理の終了を宣言
```

task_funcs
```
非同期で実行したい関数をあとで入れるためのdict(JSのObjectやMapに相当)
```
]

---

### 6. 実装したものを使ってCeleryもどきを構築する

.left[
排他制御(4.)とキュー(5.)が作れたので、あとはこれを使うだけ！
]

---

### add関数の定義

.left[
add関数をデコレータで非同期化する

```python
from taskfy import taskfy


@taskfy
def add(a, b):
    c = a + b
    print(c)
    return c
```

```python
taskfyは、add.delay(2, 3) ってやると、非同期で実行されるようにするやつ
```
]

---

### taskfyの定義

.left[
```python
from db import enqueue


class Task:
    def __init__(self, func):
        self.func = func

    def run(self, *args, **kwargs):
        # 普通に実行
        return self.func(*args, **kwargs)

    def delay(self, *args, **kwargs):
        func_name = self.func.__name__
        # キュー(この場合だとdatabaseディレクトリ)に引数をぶちこむ
        enqueue(func_name, *args, **kwargs)


# デコレータとして使う
def taskfy(func):
    return Task(func)

```
]

---
### workerの定義

.left[
```python
from db import dequeue, task_funcs
from add import add


def run_worker(process_number):
    # 本来なら↓の処理もデコレータに含めるけどめんどくさかった
    task_funcs['add'] = add.run

    while True:
        dequeue(process_number)
```
そのまんま
]

---

### 実装がおわった！！

---

### 7. 動かしてみる

.left[
- 使用するPythonインタプリタは3つ


- Worker 0 として使う
- Worker 1 として使う
- キューにメッセージ(引数入ったやつ)を入れるやつ

]

---

.left[

まずはworkerをおのおのたちあげる
```python
>>> from worker import run_worker
>>> run_worker(0)  # 疑似プロセスIDを0として起動
```

```python
>>> from worker import run_worker
>>> run_worker(1)
```
]

---
.left[

キューにメッセージを入れる
```python
>>> from add import add
>>> add.delay(2, 3)
```

Worker0かWorker1のどちらかに結果が出力される
]

---
.left[
```python
>>> for i in range(100):
...     add.delay(i, i)
```

こんなことをしても大丈夫
]

---
### 直接ジョブキューに引数を入れてみる

.left[
```sh
$ echo '["add", [10, 20], {}]' > database/test
```

これでもWorkerさえ動いていれば動く。すばらしい

これを見るとメッセージがなぜメッセージということがよくわかる
]

---

### 8. |Celeryもどきを実装した結果| ┗(☋｀ )┓三

---

もしこれで終われるなら世の中ちょろい

---

### この実装の問題点

.left[
- 2プロセスまでしか使えない(デッカーのアルゴリズムを拡張すれば解決はする)
- クソパフォーマンスなので実用できない
- 便利に活用するためにはやることがたくさん
- 普通のデータベースシステム使いたい
- テストないしいつ壊れるかわからないから怖すぎ
- turn 1で、1が1になっている状態からWorker0を起動するとデッドロックする(毎回初期化すればいけるけど……)
]

---

```
( ◠‿◠ )☛ そこに気付いたか。貴様には死んでもらう
```

---

```
▂▅▇█▓▒░('ω')░▒▓█▇▅▂うわあああああああああああ
```

---

おわり
