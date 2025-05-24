<template>
  <div class="chat-container">
    <ScrollArea type="scroll" :ref="'wrapperRef'" id="timeline-chat" class="h-72">
      <div id="wrapper-timeline-chat">
        <BoxMessage v-for="item in messageStore.messages" :success="item.success" :message="item.content"
          :role="item.role" :created_at="item.created_at" />

        <BoxMessage v-if="isBody" :message="'Carregando...'" :role="'AI'" />
      </div>

    </ScrollArea>

    <form id="input-chat" class="input-chat" @submit="submit">
      <Textarea ref="textareaRef" v-model="question" placeholder="Escreva sua dúvida" @keydown.enter="onEnter" />
      <Button @click="submit" type="submit" :disabled="questionIsEmpty() || disabledSubmit"
        style="height: auto; height: 65px; bottom: 0; position: relative;">
        <Send :size="14" />
        Enviar
      </Button>

    </form>

  </div>
</template>

<script lang="ts" setup>
import { ref } from 'vue'
import { Button } from '@/components/ui/button'
import { Textarea } from '@/components/ui/textarea'
import BoxMessage from '~/components/chat/BoxMessage.vue'
import { toast } from 'vue-sonner'
import ScrollArea from '~/components/ui/scroll-area/ScrollArea.vue'
import { Send } from 'lucide-vue-next'

const question = ref('Qual valor dos modelos o3 mini 2025-01-31 Global e o1 2024-12-17 US/EU – Data Zones?')
const disabledSubmit = ref(false)
const isBody = ref(false)
const textareaRef = ref<HTMLElement | null>(null)
const messageStore = useMessageStore()


function scrollBottom(element = '[data-slot="scroll-area-viewport"]') {
  const wrapper = document.querySelector(element)
  const el = wrapper
  if (el) {
    el.scrollTo({ behavior: 'smooth', top: el.scrollHeight + 1000 })

  }
}

function questionIsEmpty() {
  return question.value.trim() === ''
}

function onEnter(e: KeyboardEvent) {
  if (!e.shiftKey) {
    e.preventDefault()
    if (questionIsEmpty()) return
    submit()
  }
}

async function submit() {
  try {
    disabledSubmit.value = true
    isBody.value = true
    const body = {
      question: question.value,
      chat_history: messageStore.messages
    }


    messageStore.addMessage({
      created_at: new Date(),
      content: question.value,
      role: 'USER',
    })

    question.value = ''

    const chat_history = JSON.parse(JSON.stringify(messageStore.messages))
    chat_history.pop()

    const response = await $fetch('/api/data', { method: "POST", body })

    if (response.answer) {
      messageStore.addMessage({
        created_at: new Date(),
        content: response.answer as string,
        role: 'AI',
      })
    }

    scrollBottom()

  } catch (error: any) {
    const message = error.message || 'Erro ao conectar com o serviço de IA'
    messageStore.addMessage({
      created_at: new Date(),
      content: message,
      role: 'AI',
      success: false
    })
    toast(message, {
      position: "top-right",
      action: {
        label: 'Undo',
        onClick: () => console.log('Undo'),
      },
    })
  } finally {
    disabledSubmit.value = false
    isBody.value = false
    textareaRef.value?.focus()
  }
}


</script>

<style>
.chat-container {
  display: flex;
  flex-direction: column;
  height: 100%;
  gap: 10px;
  background: transparent;
}

#wrapper-timeline-chat {
  gap: 10px;
  display: flex;
  padding: 1rem;
  flex-direction: column;
}

#timeline-chat {
  flex: 1;
}

.input-chat {
  display: flex;
  gap: 10px;
  width: 100%;
  align-items: end;
}

textarea {
  border: 1px solid #5d6272;
}

textarea::placeholder {
  color: #fff;
}
</style>