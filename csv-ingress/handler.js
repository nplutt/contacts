'use strict';
const csv = require('csv-parser');
const axios = require('axios');
const AWS = require('aws-sdk');
const Readable = require('stream').Readable;

const s3 = new AWS.S3();
const lambda = new AWS.Lambda();
const bufferStream = new Readable;
const bucketName = process.env.BUCKET_NAME;
// const fileName = '279d3dbd-60c7-46f4-90a7-5f94d6451f24.csv';
const fileName = 'test_file_1.csv';
const url = 'https://eaa2qsuq62.execute-api.us-west-2.amazonaws.com/api/users';


async function main(event, context, callback) {
  console.info('Received event body of ', event);

  const fileData = await getFile(fileName);
  console.info(fileData);

  let requiredHeaderNames = {
    firstName: null,
    lastName: null,
    email: null
  };

  bufferStream.push(fileData.Body);
  bufferStream.push(null);

  bufferStream
    .pipe(csv())
    .on('headers', function(headerList) {
      requiredHeaderNames = getRequiredHeaders(headerList, requiredHeaderNames);

      if (requiredHeaderNames.firstName === null ||
          requiredHeaderNames.lastName === null ||
          requiredHeaderNames.email === null) {
        console.error("Invalid csv file, missing either first name, last name, or email address");
        throw new Error("Invalid csv file headers")
      }
    })
    .on('data', function (data) {
      pushRecord(data, requiredHeaderNames);
      // console.log(data);
      // console.log(requiredHeaderNames);
    });

  callback(null, 'Success!');
}


async function getFile(bucketKey) {
  try {
    const params = {
      Bucket: 'contacts-nplutt',
      Key: bucketKey
    };
    return await s3.getObject(params).promise();
  } catch(err) {
    console.log(err);
  }
}


async function pushRecord(row, requiredHeaderNames) {
  if (validRow(row, requiredHeaderNames)) {
    const data = formatRowData(row, requiredHeaderNames);
    try {
      console.log('POST to ', url);
      const response = await axios.post(url, data);
      console.log(response.data);
    } catch(err) {
      console.log(err);
    }
  } else {
    console.warn("Invalid row found, skipping saving to database.")
  }
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
  return row[requiredHeaderNames.firstName] !== null && row[requiredHeaderNames.firstName] !== undefined &&
    row[requiredHeaderNames.lastName] !== null && row[requiredHeaderNames.lastName] !== undefined &&
    row[requiredHeaderNames.email] !== null && row[requiredHeaderNames.email] !== undefined
}

main(null, null, null);
