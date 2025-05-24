import { defineStore } from 'pinia';
import type { Message } from '@/types/ChatMessages';

type State = {
  messages: Message[]
}

export const useMessageStore = defineStore('messages', {
  state: (): State => ({
    messages: []
  }),

  actions: {
    addMessage(message: Message) {
      this.messages.push({ ...message, success: true });
    },
    clearMessages() {
      this.messages = [];
    }
  },
})
