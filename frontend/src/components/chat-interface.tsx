"use client"

import { useState } from "react"
import { useMutation } from "@tanstack/react-query"
import { toast } from "sonner"
import { Send } from "lucide-react"

import { fetchApi } from "@/lib/api"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"

interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
}

interface ChatRequest {
  document_id: number;
  question: string;
}

const postChatMessage = async (data: ChatRequest) => {
  return fetchApi('/chat/', {
    method: 'POST',
    body: JSON.stringify(data),
  });
};

export function ChatInterface({ documentId, documentName }: { documentId: number | null, documentName: string | null }) {
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [input, setInput] = useState("")

  const mutation = useMutation({
    mutationFn: postChatMessage,
    onSuccess: (data) => {
      setMessages((prev) => [...prev, { role: 'assistant', content: data.answer }])
    },
    onError: (error: Error) => {
      toast.error(error.message)
    },
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!input.trim() || !documentId) return

    setMessages((prev) => [...prev, { role: 'user', content: input }])
    mutation.mutate({ document_id: documentId, question: input })
    setInput("")
  }

  if (!documentId) {
    return (
      <Card className="h-full flex items-center justify-center">
        <CardContent>
          <p className="text-muted-foreground">Select a document to start chatting.</p>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card className="flex flex-col h-[600px]">
      <CardHeader>
        <CardTitle>Chat with: {documentName}</CardTitle>
      </CardHeader>
      <CardContent className="flex-grow overflow-y-auto space-y-4">
        {messages.map((msg, index) => (
          <div key={index} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div className={`p-2 rounded-lg ${msg.role === 'user' ? 'bg-primary text-primary-foreground' : 'bg-muted'}`}>
              {msg.content}
            </div>
          </div>
        ))}
      </CardContent>
      <form onSubmit={handleSubmit} className="p-4 border-t flex items-center gap-2">
        <Input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask a question about the document..."
          disabled={mutation.isPending}
        />
        <Button type="submit" disabled={mutation.isPending}>
          <Send className="h-4 w-4" />
        </Button>
      </form>
    </Card>
  )
}
