# Contacts
Allows users to upload a csv containing contact details and allows them to be searched by
any data field.

![Alt text](https://github.com/nplutt/contacts/blob/master/Contacts.jpg)


## API
All endpoints with GET methods support paging using `limit` and `offset` query params. The 
`limit` value is not required but defaults to 25 and same with the `offset` value which 
defaults to 0. If the returned `count` value is equal to the `limit` value, that means there
are more records available.

* `/user?searchText="nick"&searchField="firstName"&limit=2&offset=1`
```javascript
{
  "POST": {
    "firstName": "nick",
    "lastName": "plutt",
    "emailAddress": "nplutt@gmail.com",
    "metaData": [
      {
        "fieldType": "phone number",
        "fieldData": "612-709-5521"
      }
  },
  "GET": {
    "meta": {
      "limit": 25,
      "offset": 0,
      "count": 25
    },
    "data": [
      {
        "firstName": "nick",
        "lastName": "plutt",
        "emailAddress": "nplutt@gmail.com",
        "metaData": [
          {
            "fieldType": "phone number",
            "fieldData": "612-709-5521"
          }
        ]
      }
    ]
  }
}
```

* `/user/{user_id}`
```javascript
{
  "GET": {
    "meta": {
      "limit": 25,
      "offset": 0,
      "count": 1
    },
    "data": {
      "firstName": "nick",
      "lastName": "plutt",
      "emailAddress": "nplutt@gmail.com",
      "metaData": [
        {
          "fieldType": "phone number",
          "fieldData": "612-709-5521"
        }
      ]
    }
  },
  "DELETE": { }
}
```

* `/upload`
```javascript
{
  "POST": {
    "Upload raw CSV file octet-stream in body": {}
  }
}
```

## Database
The database is an AWS RDS instance running PostgreSQL. The database is maintained and 
created using Alembic migrations. If you would like to see the database schema it is defined
[here](https://github.com/nplutt/contacts/blob/master/contacts-api/chalicelib/models/db.py).

## API Quickstart
```bash
$ mkvirtualenv contacts
$ cd contacts-api
$ pip install -Ur requirements.txt -Ur dev-requirements.txt
$ ./run_local.sh 
```

#### Run Tests
```bash
pytest -v test/
```

