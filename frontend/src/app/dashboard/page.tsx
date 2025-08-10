"use client"

import { useState } from "react"
import { useAuthStore } from "@/store/auth"
import { DocumentUpload } from "@/components/document-upload"
import { DocumentList } from "@/components/document-list"
import { ChatInterface } from "@/components/chat-interface"

interface Document {
  id: number;
  filename: string;
  created_at: string;
}

export default function DashboardPage() {
  const { user } = useAuthStore()
  const [selectedDoc, setSelectedDoc] = useState<Document | null>(null)

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Dashboard</h1>
        <p className="text-muted-foreground">
          Welcome back, <strong>{user?.full_name || user?.email}</strong>!
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <div className="space-y-6">
          <div className="space-y-4">
            <div>
              <h2 className="text-2xl font-semibold">1. Upload a Document</h2>
              <p className="text-sm text-muted-foreground">
                Upload a new PDF, TXT, or DOCX file.
              </p>
            </div>
            <DocumentUpload />
          </div>

          <div className="space-y-4">
            <div>
              <h2 className="text-2xl font-semibold">2. Select a Document</h2>
              <p className="text-sm text-muted-foreground">
                Click on a document to start a chat session.
              </p>
            </div>
            <DocumentList onDocumentSelect={setSelectedDoc} selectedDocumentId={selectedDoc?.id} />
          </div>
        </div>

        <div className="space-y-4">
           <div>
            <h2 className="text-2xl font-semibold">3. Chat</h2>
            <p className="text-sm text-muted-foreground">
              Ask questions about your selected document.
            </p>
          </div>
          <ChatInterface documentId={selectedDoc?.id} documentName={selectedDoc?.filename} />
        </div>
      </div>
    </div>
  )
}
