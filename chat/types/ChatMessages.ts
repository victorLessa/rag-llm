export type Message = {
  created_at: Date,
  content: string,
  role: "AI" | "USER",
  success?: boolean,
}