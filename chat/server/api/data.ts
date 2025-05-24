import RagService from '../service/rag'

export default defineEventHandler(async (event): Promise<any> => {
  const { question, chat_history } = await readBody(event)

  const result = await RagService.invoke(question, chat_history)

  return result


})