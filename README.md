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


