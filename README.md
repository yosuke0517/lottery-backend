# lottery-backend
# システム要件
### サブスクリプション宝くじ当選番号検索アプリ
- 会員登録することで1ヶ月間フリー検索が可能。（自動課金制）

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

# デプロイ
### ベースリソースの構築
- `01_base_resources_cfn.yaml`

### EKSクラスターの構築

```
eksctl create cluster \
 --vpc-public-subnets { CloudFormation 出力タブ WorkerSubnetsの値 } \
 --name eks-work-cluster \
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
- `kubectl port-forward nginx-pod 8080:80`
- `http://localhost:8080`へアクセス
- nginxの画面が表示されることを確認する
- `kubectl delete pod nginx-pod`で片付け

### データベースの構築
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
  - セッションマネージャーから`セッションを開始する`を選択
  - git, PostgreSQLクライアントのインストール
    - `sudo yum install -y git`
    - `sudo amazon-linux-extras install -y postgresql10`
    
- エンドポイントの確認
  - 出力タブの`RDSEndpoint`に記載
  
- データベース管理者（rootユーザ）パスワードの確認
  - CloudFormationでデータベースを構築する際、RDSの管理者パスワードをSecrets Managerが作成しデータベースに登録している
  - マネジメントコンソールのSecrets Managerの画面から確認する
  - `RdsMasterSecret`という名前で作成しているのでリンクをクリックして表示
  - `シークレットの値を取得する`ボタンを押下すると秘匿情報が表示される

- アプリケーション用データベースユーザのパスワードの確認
  - `RdsUserSecret`という名前で作成しているのでリンクを上記と同じように確認する
  
- postgresクライアントにてアプリケーション用データベースユーザの作成
  - `createuser -d -U eksdbadmin -P -h eks-work-db.cllz5clgd9hh.ca-central-1.rds.amazonaws.com mywork`
  - `createuser -d -U {ルートユーザ名} -P -h {RDSエンドポイント} {作成するユーザ名}`
  - 最初の2回は`RdsUserSecret`のパスワード
  - 最後の1回は`RdsMasterSecret`のパスワード
  
- データベースの作成
  - `createdb -U mywork -h eks-work-db.cllz5clgd9hh.ca-central-1.rds.amazonaws.com -E UTF8 myworkdb`
  - パスワード入力を促されるので`RdsUserSecret`のパスワードを入力する
  
- データベースへの接続とDDLの実行
  - `psql -U mywork -h eks-work-db.cllz5clgd9hh.ca-central-1.rds.amazonaws.com myworkdb`
  
- マイグレーション
  - TODO 1154~