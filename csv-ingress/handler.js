'use strict';
const async = require('async');
const axios = require('axios');
const AWS = require('aws-sdk');
const csv = require('csv-parser');
const Readable = require('stream').Readable;

const s3 = new AWS.S3();
const lambda = new AWS.Lambda();
const bucketName = process.env.BUCKET_NAME;
const url = 'https://eaa2qsuq62.execute-api.us-west-2.amazonaws.com/api/users';


exports.handler = function(event, context, callback) {
  console.info('Received event body of ', event);

  let s3Key = null;
  let index = 0;
  let fileIndex = 0;
  let processedRecords = 0;

  if (event.Records) {
    s3Key = event.Records[0].s3.object.key;
  } else {
    s3Key = event.s3Key;
    index = event.index;
  }

  async.waterfall([
    function getFile(next) {
      const params = {
        Bucket: bucketName,
        Key: s3Key
      };
      s3.getObject(params, (err, data) => {
        next(err, data);
      });
    },
    function processData(fileData, next) {
      let calls = [];
      let requiredHeaderNames = {
        firstName: null,
        lastName: null,
        email: null
      };

      const bufferStream = new Readable;
      bufferStream.push(fileData.Body);
      bufferStream.push(null);

      bufferStream
        .pipe(csv())
        .on('headers', function(headerList) {
          requiredHeaderNames = getRequiredHeaders(headerList, requiredHeaderNames);

          if (requiredHeaderNames.firstName === null ||
            requiredHeaderNames.lastName === null ||
            requiredHeaderNames.email === null) {
            console.error('Invalid csv file, missing either first name, last name, or email address');
            throw new Error('Invalid csv file headers')
          }
        })
        .on('data', function (row) {
          if (fileIndex >= (index + processedRecords) && processedRecords < 50 && validRow(row, requiredHeaderNames)) {
            const data = formatRowData(row, requiredHeaderNames);
            calls.push(makeCall(url, data));
            processedRecords ++;
          }
          fileIndex ++;
        })
        .on('end', function() {
          axios.all(calls).then((res) => {
            console.log(res);
            next();
          }).catch((err) => {
            console.info(err);
            next();
          });
        });
    },
    function invokeLambda(next) {
      console.info("Sleeping for 5 seconds so as not to overwhelm the db");
      index += processedRecords;

      const params = {
        FunctionName: 'csv-ingress-dev-csv-ingress',
        Payload: JSON.stringify({
          index: index,
          s3Key: s3Key
        }),
        InvocationType: 'Event'
      };

      if ((processedRecords + index) < fileIndex){
        setTimeout(() => {
          console.info("Invoking lambda to continue processing records");
          lambda.invoke(params, (err, res) => {
            if (err) {
              console.info(err);
            }
            next(err, res);
          });
        }, 5000);
      } else {
        next();
      }
    }
  ], (err, res) => {
    if (err) {
      console.error('Failed to process contact file.');
    } else {
      console.info('Succeeded in processing 50 records')
    }
    callback(null, 'Success!')
  });
};


function makeCall(url, data) {
  return axios.post(url, data)
}


function formatRowData(row, requiredHeaderNames) {
  let data = {
    firstName: row[requiredHeaderNames.firstName],
    lastName: row[requiredHeaderNames.lastName],
    emailAddress: row[requiredHeaderNames.email],
    metaData: []
  };

  Object.keys(row).forEach(function(key) {
    if ((key !== requiredHeaderNames.firstName) && (key !== requiredHeaderNames.lastName)
      && (key !== requiredHeaderNames.email)) {
      data.metaData.push({
        dataType: key,
        data: row[key]
      });
    }
  });

  return data;
}


function getRequiredHeaders(headers, requiredHeaderNames) {
  let headersLower = headers.map(v => v.toLowerCase());

  if (headersLower.indexOf('firstname') > -1) {
    requiredHeaderNames.firstName = headers[headersLower.indexOf('firstname')];
  } else if (headersLower.indexOf('first name') > -1) {
    requiredHeaderNames.firstName = headers[headersLower.indexOf('first name')];
  } else if (headersLower.indexOf('first') > -1) {
    requiredHeaderNames.firstName = headers[headersLower.indexOf('first')];
  }

  if (headersLower.indexOf('lastname') > -1) {
    requiredHeaderNames.lastName = headers[headersLower.indexOf('lastname')];
  } else if (headersLower.indexOf('last name') > -1) {
    requiredHeaderNames.lastName = headers[headersLower.indexOf('last name')];
  } else if (headersLower.indexOf('last') > -1) {
    requiredHeaderNames.lastName = headers[headersLower.indexOf('last')];
  }

  if (headersLower.indexOf('emailaddress') > -1) {
    requiredHeaderNames.email = headers[headersLower.indexOf('emailaddress')];
  } else if (headersLower.indexOf('email address') > -1) {
    requiredHeaderNames.email = headers[headersLower.indexOf('email address')];
  } else if (headersLower.indexOf('email') > -1) {
    requiredHeaderNames.email = headers[headersLower.indexOf('email')];
  }

  return requiredHeaderNames;
}


function validRow(row, requiredHeaderNames) {
  const valid = row[requiredHeaderNames.firstName] !== null && row[requiredHeaderNames.firstName] !== undefined &&
    row[requiredHeaderNames.lastName] !== null && row[requiredHeaderNames.lastName] !== undefined &&
    row[requiredHeaderNames.email] !== null && row[requiredHeaderNames.email] !== undefined;

  if (!valid) {
    console.warn('Invalid row found, skipping saving to database.');
  }

  return valid
}
