from rasa_sdk import Tracker
from rasa_sdk.executor import CollectingDispatcher

from typing import Dict, Text, Any, List

import requests
from rasa_sdk import Action
from rasa_sdk.events import  Form, SlotSet, FollowupAction , ActionExecuted ,UserUttered
from rasa.core.constants import REQUESTED_SLOT
from rasa_sdk.forms import FormAction
import json 
from datetime import datetime 
from decimal import *


class ActionResetAllSlots(Action):

    def name(self):
        return "action_reset_all_slots"

    def run(self, dispatcher, tracker, domain):
        return [SlotSet("user_message", None),SlotSet("user_name", None)]

class LookUser(Action):

    def name(self):
        return "LookUser"

    def run(self, dispatcher, tracker, domain):
        intent= tracker.latest_message['intent'].get('name')                
        name = ''
        latest_name = ''
        getname = tracker.get_latest_entity_values('PERSON')
        while name != None:
          latest_name = name          
          name = next(getname, None)   
        print(latest_name)                                                         
        if latest_name != None and len(latest_name) != 0:
          dispatcher.utter_message(template="utter_{}".format(intent),calling_person = latest_name)
          return [SlotSet("calling_person",latest_name), SlotSet("user_message", None),SlotSet("user_name", None)]        
        if tracker.get_slot("calling_person") == None:
          dispatcher.utter_message(template="utter_{}".format(intent),calling_person = "Richard")
          return [SlotSet("user_message", None),SlotSet("user_name", None)]
        dispatcher.utter_message(template="utter_{}".format(intent))
        return  [SlotSet("user_message", None),SlotSet("user_name", None)]

class InformUser(FormAction):
    def name(self):
        return "InformUser"

    @staticmethod
    def required_slots(tracker: Tracker) -> List[Text]:
        return ["user_message" ,
                # "user_name"
                ]
    
    def slot_mappings(self):
        return {"user_message": self.from_entity(entity="user_message",
                                             intent=["leaving_message"]),
                # "user_name": self.from_entity(entity="PERSON",
                #                              intent=["leaving_message","name",'callback']),                                                           
                                            }

    def request_next_slot(self, dispatcher, tracker, domain):
        
        print(tracker.get_slot("calling_person"),tracker.get_slot("PERSON"),tracker.get_slot("user_name"), tracker.get_slot("user_message"))
        for slot in self.required_slots(tracker):
            if self._should_request_slot(tracker, slot):                
                dispatcher.utter_message(template="utter_ask_{}".format(slot))
                return [SlotSet(REQUESTED_SLOT, slot)]
        return None

    # def validate_user_name(
    #     self,
    #     value: Text,
    #     dispatcher: CollectingDispatcher,
    #     tracker: Tracker,
    #     domain: Dict[Text, Any],
    # ) -> Dict[Text, Any]: 
    #   try: 
    #     if isinstance(value,str):
    #       return {"user_name": value}
    #     else:
    #       set_value = list(set(value))
    #       print("user_name", set_value)
    #       if len(set_value) == 1:
    #         print('str')
    #         return {"user_name": set_value[0]}
    #       elif len(set_value) > 1:
    #         print('lst')
    #         return {"user_name": None}
    #       else:
    #         return {"user_name": value}
    #   except:
    #       return {"user_name": None}
        
        
        
    async def validate(self, dispatcher, tracker, domain):        
      latest_message = tracker.latest_message.get('text').strip().lower()
      slot_values = self.extract_other_slots(dispatcher, tracker, domain)

      slot_to_fill = tracker.get_slot(REQUESTED_SLOT)
      
      # if not slot_values:
      #     # reject to execute the form action
      #     # if some slot was requested but nothing was extracted
      #     # it will allow other policies to predict another action
      #     raise ActionExecutionRejection(
      #         self.name(),
      #         f"Failed to extract slot {slot_to_fill} with action {self.name()}."
      #         f"Allowing other policies to predict next action.",
      #     )

      if slot_to_fill == 'user_message':        
        slot_values.update({"user_message":latest_message,
                           "user_name":None})
      # if slot_to_fill == 'user_name':        
      #   slot_values.update({"user_name":latest_message})
      if slot_to_fill:        
        print(self.extract_requested_slot(dispatcher, tracker, domain))
        slot_values.update(self.extract_requested_slot(dispatcher, tracker, domain))
        if not slot_values:
          tracker.active_form = {}
          tracker.slots["requested_slot"] = None
          # dispatcher.utter_message(template="utter_something_went_wrong")
      return await self.validate_slots(slot_values, dispatcher, tracker, domain)
    

    def submit(self,
               dispatcher: CollectingDispatcher,
               tracker: Tracker,
               domain: Dict[Text, Any]) -> List[Dict]:
        """Define what the form has to do
            after all required slots are filled"""
        
        # dispatcher.utter_message(f'i am going to :\n - user_message: {tracker.get_slot("user_message")}\n user_name: {tracker.get_slot("user_name")}')
        dispatcher.utter_message(template="utter_leaving_message")           
        return_slots = [Form(None),SlotSet("user_message", None),SlotSet("user_name", None)]
        return return_slots