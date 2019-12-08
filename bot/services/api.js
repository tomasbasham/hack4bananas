"use strict";

const request = require("request");

module.exports = class API {
    static connectAPI(image, callback) {
        var options = {
            uri: 'http://964afd39.ngrok.io/predict',
            method: 'POST',
            json: image
        };
        // request.get('http://hack4bananas.herokuapp.com/predict', image, callback);
        // console.log(options);
        // request.post('http://19a8e53a.ngrok.io/predict', JSON.stringify(image), callback);

        request(options, callback);
    }
}
