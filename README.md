# lottery-backend
# システム要件
### サブスクリプション宝くじ当選番号検索アプリ
- ~~会員登録することで1ヶ月間フリー検索が可能。（自動課金制）~~

# テーブル設計
- [テーブル設計](https://docs.google.com/spreadsheets/d/1qf94PoMqfEpVkMwJFre9tEFsBqO0vTpGz5La-3Ukxks/edit#gid=0)

### 決済について
- pay.jpに一任する
- [参考](https://qiita.com/k4ssyi/items/5df5ea12cdffc9597198)

# 未使用のボリュームを削除
$ docker volume prune

### migrationファイル削除
- `find . -path "*/migrations/*.py" -not -name "__init__.py" -delete`

### マイグレーションファイル作成
- `docker-compose run web python manage.py makemigrations`

### マイグレーション実施
- `docker-compose run web python manage.py migrate`

### スーパーユーザ作成
- `docker-compose run web python manage.py createsuperuser`

### データベース接続
- `psql -U lottery -d lotterydb -h localhost`
- テーブル一覧：`\dt`

# 💴デプロイ💴
## ベースリソースの構築
- `01_base_resources_cfn.yaml`

## EKSクラスターの構築
- `--name`のsuffixは自動的に`-cluster`が付与されるので明示的に-clusterを付与しない方が良い（-cluster-clusterってなる）
```
eksctl create cluster \
 --vpc-public-subnets { CloudFormation 出力タブ WorkerSubnetsの値 } \
 --name eks-work \
 --region ca-central-1 \
 --version 1.14 \
 --nodegroup-name eks-work-nodegroup \
 --node-type t2.small \
 --nodes 2 \
 --nodes-min 2 \
 --nodes-max 5
```

### 上記までの動作確認
- `kubectl apply -f eks-env/02_nginx_k8s.yaml`
- `kubectl port-forward nginx-pod 8000:80`
- `http://localhost:8000`へアクセス
- nginxの画面が表示されることを確認する
- `kubectl delete pod nginx-pod`で片付け

## データベースの構築
##### おおまかな手順

```
- データベースと踏み台サーバを構築する
- SessionManagerを用いて踏み台サーバにアクセスする
- 踏み台サーバ上に必要なツールを導入する
- 踏み台サーバ上でGitリポジトリをクローンする
- データベースに接続し、DDL及びサンプルデータの投入を行う
```

- スタックの作成
  - `10_rds_ope_cfn.yaml`をコンソールから読み込ませて作成する
  - `EksWorkVPC`には`ベースリソースの構築`にて作成したVPCを選択する
  - `OpeServerRouteTable`には`ベースリソースの構築`にて作成したルートテーブルを指定する
    - `eks-work-base`の`出力タブ`→`RouteTable`がキーになっている値部分
  - `スタックオプションの設定`は特に変更なし
  - `レビュー eks-work-rds`にて`AWS CloudFormation によって IAM リソースがカスタム名で作成される場合があることを承認します。`にチェックを入れて`スタックの作成`
  - 踏み台サーバも作成される
  
- セッションマネージャーによる踏み台サーバへの接続
  - System Manager→セッションマネージャーから`セッションを開始する`を選択
  - git, PostgreSQLクライアントのインストール
    - `sudo yum install -y git`
    - `sudo amazon-linux-extras install -y postgresql10`
    - `cd`でホームディレクトリへ移動
    
- エンドポイントの確認
  - 出力タブの`RDSEndpoint`に記載
  
- データベース管理者（rootユーザ）パスワードの確認
  - CloudFormationでデータベースを構築する際、RDSの管理者パスワードをSecrets Managerが作成しデータベースに登録している
  - マネジメントコンソールのSecrets Managerの画面から確認する
  - `RdsMasterSecret`という名前で作成しているのでリンクをクリックして表示
  - `シークレットの値を取得する`ボタンを押下すると秘匿情報が表示される

- アプリケーション用データベースユーザのパスワードの確認
  - `RdsUserSecret`という名前で作成しているのでリンクを上記と同じように確認する
  
- postgresクライアントにてアプリケーション用データベースユーザの作成（セッションマネージャーにて作業）
  - `createuser -d -U eksdbadmin -P -h {RDS EndPoint} mywork`
  - `createuser -d -U {ルートユーザ名} -P -h {RDSエンドポイント} {作成するユーザ名}`
  - 最初の2回は`RdsUserSecret`のパスワード
  - 最後の1回は`RdsMasterSecret`のパスワード
  
- データベースの作成（セッションマネージャーにて作業）
  - `createdb -U mywork -h {RDS EndPoint} -E UTF8 myworkdb`
  - パスワード入力を促されるので`RdsUserSecret`のパスワードを入力する
  
- データベースへの接続とDDLの実行（セッションマネージャーにて作業）
  - `psql -U mywork -h {RDS EndPoint} myworkdb`
  
## マイグレーション
- どうしようか迷ったが、踏み台サーバにdocker, docker-composeを入れてマイグレーションすることにした
  - [参考](https://qiita.com/TakumaKurosawa/items/e67315583009257cd1ea)
- docker-compose.yml
  - dbとvolumeは消さないといけない
- setting.py
  - 接続先情報を本番用に書き直さないといけない（環境変数で注入できなかった・・・）

- ■docker-compose.yml
```

version: '3'
services:
  web:
    container_name: lottery_api
    build: .
    command: ["./wait-for-it.sh", "{RDSエンドポイント}", "--", "python", "manage.py", "runserver", "0.0.0.0:8000"]
    ports:
      - "8000:8000"
    volumes:
      - .:/app
    tty: true
    stdin_open: true

```
- ■setting.py
```
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': '{本番用データベース名}',
        'USER': '{本番用ユーザ}',
        'PASSWORD': '{本番用DBパスワード}',
        'HOST': '{本番用エンドポイント}',
        'PORT': 5432
    }
}
```
- `docker-compose_production.yml`としてローカルに配置している
- `lottery_backend/setting_production.py`としてローカルに配置している

# ec2のユーザデータで初期化
```
#!/bin/bash

# ホスト名
sed -i 's/^HOSTNAME=[a-zA-Z0-9\.\-]*$/HOSTNAME={ホスト名}/g' /etc/sysconfig/network
hostname '{ホスト名}'

# タイムゾーン
cp /usr/share/zoneinfo/Japan /etc/localtime
sed -i 's|^ZONE=[a-zA-Z0-9\.\-\"]*$|ZONE="Asia/Tokyo”|g' /etc/sysconfig/clock

# 言語設定
echo "LANG=ja_JP.UTF-8" > /etc/sysconfig/i18n

```

# 設定ファイルを分ける
- settingsフォルダを作成し既存のsettings.pyをbase.pyへリネーム
- __init__.pyを作成（pyCharmなら自動作成される）
- local.py,production.pyを作成（分けたい項目をbase.pyから削除してそれぞれに書く）
  - 共通で使用するものはそのままbase.py

### runserverやmigrate時の設定ファイルの渡し方
  - `python3 manage.py migrate --settings lottery_backend.settings.production`
    - 上記のように`--settings`オプションを渡して各環境の場所を指定する
    - 上記ではlottery_backend/settings/production.pyの設定ファイルを読み込んでいる（base.pyは指定しなくて良い）

### Wsgiサーバーとしてgunicornを導入する
- pipenv install gunicorn
- 設定ファイル（wsgi.pyの設定ファイル参照を以下のように編集）

```
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lottery_backend.settings.production')
```

### nginxとgunicornを接続
- /etc/nginx/nginx.conf
```
# For more information on configuration, see:
#   * Official English Documentation: http://nginx.org/en/docs/
#   * Official Russian Documentation: http://nginx.org/ru/docs/

user nginx;
worker_processes auto;
error_log /var/log/nginx/error.log;
pid /var/run/nginx.pid;

# Load dynamic modules. See /usr/share/doc/nginx/README.dynamic.
include /usr/share/nginx/modules/*.conf;

events {
    worker_connections 1024;
}

http {


    include             /etc/nginx/mime.types;
    default_type        application/octet-stream;

    # Load modular configuration files from the /etc/nginx/conf.d directory.
    # See http://nginx.org/en/docs/ngx_core_module.html#include
    # for more information.
    include /etc/nginx/conf.d/*.conf;

    index   index.html index.htm;

    upstream app_server {
       server 127.0.0.1:8000 fail_timeout=0;
    }

    server {

        ## ここを書き換える
        listen    80;
        server_name     (EC2のドメイン or IPアドレス);
        client_max_body_size    6G;

        # Load configuration files for the default server block.
        include /etc/nginx/default.d/*.conf;

        location / {
            # 以下4行を追加
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header Host $http_host;
            proxy_redirect off;
            proxy_pass   http://app_server;
        }

        location /static {
            alias (アプリケーションのstaticファイルの絶対パスを記入);
            expires 5h;
        }

        # redirect server error pages to the static page /40x.html
        #
        error_page 404 /404.html;
            location = /40x.html {
        }

        # redirect server error pages to the static page /50x.html
        #
        error_page 500 502 503 504 /50x.html;
            location = /50x.html {
        }

        # proxy the PHP scripts to Apache listening on 127.0.0.1:80
        #
        #location ~ \.php$ {
        #    proxy_pass   http://127.0.0.1;
        #}

        # pass the PHP scripts to FastCGI server listening on 127.0.0.1:9000
        #
        #location ~ \.php$ {
        #    root           html;
        #    fastcgi_pass   127.0.0.1:9000;
        #    fastcgi_index  index.php;
        #    fastcgi_param  SCRIPT_FILENAME  /scripts$fastcgi_script_name;
        #    include        fastcgi_params;
        #}

        # deny access to .htaccess files, if Apache's document root
        # concurs with nginx's one
        #
        #location ~ /\.ht {
        #    deny  all;
        #}
    }

}


```

- nginx再起動
  - `sudo service nginx restart`
  
- これでClient -> Server80番ポート(Nginx) -> Server8000番ポート(gunicorn) -> Djangoアプリケーション
の流れを作ることができる

### gunicorn起動
- `gunicorn lottery_backend.wsgi --bind=0.0.0.0:8000`