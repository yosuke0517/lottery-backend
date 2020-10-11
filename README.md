# lottery-backend
# システム要件
### サブスクリプション宝くじ当選番号検索アプリ
- 会員登録することで1ヶ月間フリー検索が可能。（自動課金制）

# テーブル設計
- [テーブル設計](https://docs.google.com/spreadsheets/d/1qf94PoMqfEpVkMwJFre9tEFsBqO0vTpGz5La-3Ukxks/edit#gid=0)

### 決済について
- pay.jpに一任する
- [参考](https://qiita.com/k4ssyi/items/5df5ea12cdffc9597198)

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