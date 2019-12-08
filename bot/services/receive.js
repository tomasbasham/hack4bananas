/**
 * Copyright 2019-present, Facebook, Inc. All rights reserved.
 *
 * This source code is licensed under the BSD-style license found in the
 * LICENSE file in the root directory of this source tree.
 *
 * Messenger For Original Coast Clothing
 * https://developers.facebook.com/docs/messenger-platform/getting-started/sample-apps/original-coast-clothing
 */

"use strict";

const Curation = require("./curation"),
  Api = require("./api"),
  Order = require("./order"),
  Response = require("./response"),
  Care = require("./care"),
  Survey = require("./survey"),
  GraphAPi = require("./graph-api"),
  i18n = require("../i18n.config");

const recipe = {};
const image = {};
module.exports = class Receive {
  constructor(user, webhookEvent) {
    this.user = user;
    this.webhookEvent = webhookEvent;
  }

  // Check if the event is a message or postback and
  // call the appropriate handler function
  handleMessage() {
    let event = this.webhookEvent;
    let responses;

    try {
      if (event.message) {
        let message = event.message;

        if (message.quick_reply) {
          responses = this.handleQuickReply();
        } else if (message.attachments) {
          responses = this.handleAttachmentMessage(this.sendMessageWithUser);
        } else if (message.text) {
          responses = this.handleTextMessage();
        }
      } else if (event.postback) {
        responses = this.handlePostback();
      } else if (event.referral) {
        responses = this.handleReferral();
      }
    } catch (error) {
      console.error(error);
      responses = {
        text: `An error has occured: '${error}'. We have been notified and \
        will fix the issue shortly!`
      };
    }

    if (Array.isArray(responses)) {
      let delay = 0;
      for (let response of responses) {
        this.sendMessage(response, delay * 2000);
        delay++;
      }
    } else {
      this.sendMessage(responses);
    }
  }

  // Handles messages events with text
  handleTextMessage() {
    console.log(
      "Received text:",
      `${this.webhookEvent.message.text} for ${this.user.psid}`
    );

    // check greeting is here and is confident
    let greeting = this.firstEntity(this.webhookEvent.message.nlp, "greetings");

    let message = this.webhookEvent.message.text.trim().toLowerCase();

    let response;

    if (
      (greeting && greeting.confidence > 0.8) ||
      message.includes("start over")
    ) {
      response = Response.genNuxMessage(this.user);
    } else if (Number(message)) {
      response = Order.handlePayload("ORDER_NUMBER");
    } else if (message.includes("#")) {
      response = Survey.handlePayload("CSAT_SUGGESTION");
    } else if (message.includes(i18n.__("care.help").toLowerCase())) {
      let care = new Care(this.user, this.webhookEvent);
      response = care.handlePayload("CARE_HELP");
    } else {
      response = [
        Response.genText(
          i18n.__("fallback.any", {
            message: this.webhookEvent.message.text
          })
        ),
        Response.genText(i18n.__("get_started.guidance")),
        Response.genQuickReply(i18n.__("get_started.help"), [
          {
            title: i18n.__("menu.suggestion"),
            payload: "CURATION"
          },
          {
            title: i18n.__("menu.help"),
            payload: "CARE_HELP"
          }
        ])
      ];
    }

    return response;
  }

  // Example API
  test() {
    Api.connectAPI('', (err, res, body) => {
      console.log(body);
    });
  }

  getUserOptions() {
    return Response.genQuickReply(i18n.__("recipe.guidance"), [
      {
        title: i18n.__("recipe.showingredients"),
        payload: "SHOW_INGREDIENTS"
      },
      {
        title: i18n.__("recipe.showinstructions"),
        payload: "SHOW_INSTRUCTIONS"
      },
      {
        title: i18n.__("recipe.export"),
        payload: "EXPORT_RECIPE"
      },
      {
        title: i18n.__("upload.anotherpicture"),
        payload: "UPLOAD_PICTURE"
      },
    ]);
  }

  // Handles mesage events with attachments
  handleAttachmentMessage(callbackFunc) {
    // Get the attachment
    const attachment = this.webhookEvent.message.attachments[0];
    console.log("Received attachment:", `${attachment} for ${this.user.psid}`);
    Api.connectAPI(attachment.payload, (err, res, body) => {
      console.log(`Response: ${body}` );
      if (!body) return;
      // body = JSON.parse(body);
      callbackFunc(
        Response.genText(i18n.__("recipe.name", {
          name: body.name
        })), 2000, this.user);
      callbackFunc(this.getUserOptions(), 4000, this.user);
      let randomString =  Math.random().toString(36).substring(2, 15) + Math.random().toString(36).substring(2, 15);
      randomString = randomString.toUpperCase();
      recipe[this.user.psid] = body;
      recipe[this.user.psid].ref = randomString;
      recipe[recipe[this.user.psid].ref] = JSON.parse(JSON.stringify(recipe[this.user.psid]));
      image[recipe[this.user.psid].ref] = attachment.payload.url;
    });
    return Response.genText(i18n.__("upload.thinking"));
  }

  // Handles mesage events with quick replies
  handleQuickReply() {
    // Get the payload of the quick reply
    let payload = this.webhookEvent.message.quick_reply.payload;

    return this.handlePayload(payload);
  }

  // Handles postbacks events
  handlePostback() {
    let postback = this.webhookEvent.postback;
    // Check for the special Get Starded with referral
    let payload;
    if (postback.referral && postback.referral.type == "OPEN_THREAD") {
      payload = postback.referral.ref;
    } else {
      // Get the payload of the postback
      payload = postback.payload;
    }
    return this.handlePayload(payload.toUpperCase());
  }

  // Handles referral events
  handleReferral() {
    // Get the payload of the postback
    let payload = this.webhookEvent.referral.ref.toUpperCase();

    return this.handlePayload(payload);
  }

  handlePayload(payload) {
    console.log("Received Payload:", `${payload} for ${this.user.psid}`);

    // Log CTA event in FBA
    GraphAPi.callFBAEventsAPI(this.user.psid, payload);
    let response;
    if (payload === "SHOW_INGREDIENTS") {
      response = [];
      const items = recipe[this.user.psid].ingredients;
      let text = '';
      for (const i in items) {
        text += (i > 0 ? ', ' : '') + items[i];
      }
      response.push(
        Response.genText(i18n.__("recipe.text", {
          text: text
        }))
      )
      response.push(this.getUserOptions());
    } else if (payload === "SHOW_INSTRUCTIONS" || payload.startsWith("SHOW_INSTRUCTIONS")) {
        const currentStep = payload.split("SHOW_INSTRUCTIONS")[1] | '0';
        const stepNumber = parseInt(currentStep);
        response = [];
        const items = recipe[this.user.psid].steps;
        response.push(
          Response.genText(i18n.__("recipe.text", {
            text: (items[stepNumber])
          }))
        );
        if (stepNumber + 1 === items.length) {
          response.push(this.getUserOptions());
        } else {
          response.push(
            Response.genQuickReply(i18n.__("recipe.tellnext"), [
              {
                title: i18n.__("recipe.next"),
                payload: `SHOW_INSTRUCTIONS${stepNumber + 1}`
              },
              {
                title: i18n.__("recipe.finish"),
                payload: 'FINISH_INSTRUCTIONS'
              }
            ])
          );
        }
    } else if (payload === "FINISH_INSTRUCTIONS") {
      response = this.getUserOptions();
    } else if (payload === "EXPORT_RECIPE") {
      response = Response.genQuickReply(i18n.__("recipe.exportquestions"), [
        {
          title: i18n.__("recipe.sendtofriends"),
          payload: "SEND_TO_FRIENDS"
        },
        {
          title: i18n.__("recipe.buyingredients"),
          payload: "BUY_INGREDIENTS"
        },
        {
          title: i18n.__("recipe.download"),
          payload: "DOWNLOAD_RECIPE"
        },
        {
          title: i18n.__("recipe.feedback"),
          payload: "FEEDBACK_RECIPE"
        },
      ]);
    } else if (payload === "SEND_TO_FRIENDS") {
      response = [Response.genGenericTemplate(
        image[recipe[this.user.psid].ref],
        i18n.__("recipe.forward", {
          name: recipe[this.user.psid].name
        }),
        '',
        [
          Response.genWebUrlButton(
            i18n.__("recipe.getrecipe"),
            `https://m.me/106407507515158?ref=RECIPE-${recipe[this.user.psid].ref}`
          ),
        ]
      )];
    } else if (payload === "BUY_INGREDIENTS") {
      response = [Response.genGenericTemplate(
        'https://upload.wikimedia.org/wikipedia/en/thumb/b/b0/Tesco_Logo.svg/1024px-Tesco_Logo.svg.png',
        i18n.__("recipe.forward", {
          name: `${recipe[this.user.psid].name} ingredients`
        }),
        '',
        [
          Response.genWebUrlButton(
            i18n.__("recipe.buyingredients"),
            `https://m.me/106407507515158?ref=RECIPE-${recipe[this.user.psid].ref}`
          ),
        ]
      )];
    } else if (payload === "FEEDBACK_RECIPE") {
      response = Response.genQuickReply(i18n.__("feedback.question"), [
        {
          title: i18n.__("feedback.excellence"),
          payload: "AFTER_FEEDBACK"
        },
        {
          title: i18n.__("feedback.good"),
          payload: "AFTER_FEEDBACK"
        },
        {
          title: i18n.__("feedback.soso"),
          payload: "AFTER_FEEDBACK"
        },
        {
          title: i18n.__("feedback.dislike"),
          payload: "AFTER_FEEDBACK"
        },
      ]);
    } else if (payload === "AFTER_FEEDBACK") {
      response = [
        Response.genText(i18n.__("feedback.thankyou")),
        this.getUserOptions()
      ];
    } else if (payload.startsWith("RECIPE")) {
      const ref = payload.split("RECIPE-")[1];
      recipe[this.user.psid] = recipe[ref];
      response = this.getUserOptions();
    } else if (payload === "UPLOAD_PICTURE") {
      response = Response.genText(i18n.__("upload.hint"));
    } else if (payload === "NO_INTENT") {
      const misunderstand = Response.genText(i18n.__("get_started.welcome"));
      const question = Response.genQuickReply(i18n.__("get_started.guidance"), [
        {
          title: i18n.__("upload.picture"),
          payload: "UPLOAD_PICTURE"
        },
        {
          title: i18n.__("upload.other"),
          payload: "NO_INTENT"
        }
      ]);
      response = [misunderstand, question];
    }
    else if (
      payload === "GET_STARTED" ||
      payload === "DEVDOCS" ||
      payload === "GITHUB"
    ) {
      response = Response.genNuxMessage(this.user);
    } else if (payload.includes("CURATION") || payload.includes("COUPON")) {
      let curation = new Curation(this.user, this.webhookEvent);
      response = curation.handlePayload(payload);
    } else if (payload.includes("CARE")) {
      let care = new Care(this.user, this.webhookEvent);
      response = care.handlePayload(payload);
    } else if (payload.includes("ORDER")) {
      response = Order.handlePayload(payload);
    } else if (payload.includes("CSAT")) {
      response = Survey.handlePayload(payload);
    } else if (payload.includes("CHAT-PLUGIN")) {
      response = [
        Response.genText(i18n.__("chat_plugin.prompt")),
        Response.genText(i18n.__("get_started.guidance")),
        Response.genQuickReply(i18n.__("get_started.help"), [
          {
            title: i18n.__("care.order"),
            payload: "CARE_ORDER"
          },
          {
            title: i18n.__("care.billing"),
            payload: "CARE_BILLING"
          },
          {
            title: i18n.__("care.other"),
            payload: "CARE_OTHER"
          }
        ])
      ];
    } else {
      response = {
        text: `This is a default postback message for payload: ${payload}!`
      };
    }

    return response;
  }

  handlePrivateReply(type,object_id) {
    let welcomeMessage = i18n.__("get_started.welcome") + " " +
      i18n.__("get_started.guidance") + ".";

    let response = Response.genQuickReply(welcomeMessage, [
      {
        title: i18n.__("upload.picture"),
        payload: "UPLOAD_PICTURE"
      },
      {
        title: i18n.__("upload.other"),
        payload: "NO_INTENT"
      }
    ]);

    let requestBody = {
      recipient: {
        [type]: object_id
      },
      message: response
    };

    GraphAPi.callSendAPI(requestBody);
  }

  sendMessage(response, delay = 0) {
    // Check if there is delay in the response
    if ("delay" in response) {
      delay = response["delay"];
      delete response["delay"];
    }

    // Construct the message body
    let requestBody = {
      recipient: {
        id: this.user.psid
      },
      message: response
    };

    // Check if there is persona id in the response
    if ("persona_id" in response) {
      let persona_id = response["persona_id"];
      delete response["persona_id"];

      requestBody = {
        recipient: {
          id: this.user.psid
        },
        message: response,
        persona_id: persona_id
      };
    }

    setTimeout(() => GraphAPi.callSendAPI(requestBody), delay);
  }

  sendMessageWithUser(response, delay = 0, user) {
    // Check if there is delay in the response
    if ("delay" in response) {
      delay = response["delay"];
      delete response["delay"];
    }

    // Construct the message body
    let requestBody = {
      recipient: {
        id: user.psid
      },
      message: response
    };

    // Check if there is persona id in the response
    if ("persona_id" in response) {
      let persona_id = response["persona_id"];
      delete response["persona_id"];

      requestBody = {
        recipient: {
          id: user.psid
        },
        message: response,
        persona_id: persona_id
      };
    }

    setTimeout(() => GraphAPi.callSendAPI(requestBody), delay);
  }

  firstEntity(nlp, name) {
    return nlp && nlp.entities && nlp.entities[name] && nlp.entities[name][0];
  }
};
