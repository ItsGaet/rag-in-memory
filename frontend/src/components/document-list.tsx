"use client"

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query"
import { toast } from "sonner"
import { Trash2, FileText } from "lucide-react"

import { fetchApi } from "@/lib/api"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"

interface Document {
  id: number;
  filename: string;
  created_at: string;
}

const getDocuments = async (): Promise<Document[]> => {
  return fetchApi('/documents/');
};

const deleteDocument = async (documentId: number) => {
  return fetchApi(`/documents/${documentId}`, { method: 'DELETE' });
};

interface DocumentListProps {
  onDocumentSelect: (doc: Document) => void;
  selectedDocumentId: number | null | undefined;
}

export function DocumentList({ onDocumentSelect, selectedDocumentId }: DocumentListProps) {
  const queryClient = useQueryClient()
  const { data: documents, isLoading, error } = useQuery({
    queryKey: ['documents'],
    queryFn: getDocuments,
  })

  const deleteMutation = useMutation({
    mutationFn: deleteDocument,
    onSuccess: () => {
      toast.success("Document deleted successfully!")
      queryClient.invalidateQueries({ queryKey: ['documents'] })
    },
    onError: (error: Error) => {
      toast.error(error.message)
    },
  })

  if (isLoading) return <div>Loading documents...</div>
  if (error) return <div className="text-red-500">Error loading documents: {error.message}</div>

  return (
    <Card>
      <CardHeader>
        <CardTitle>Your Documents</CardTitle>
      </CardHeader>
      <CardContent>
        {documents && documents.length > 0 ? (
          <ul className="space-y-2">
            {documents.map((doc) => (
              <li
                key={doc.id}
                className={`flex items-center justify-between p-2 border rounded-md cursor-pointer transition-colors ${selectedDocumentId === doc.id ? 'bg-muted' : 'hover:bg-muted/50'}`}
                onClick={() => onDocumentSelect(doc)}
              >
                <div className="flex items-center gap-2">
                  <FileText className="h-5 w-5" />
                  <div>
                    <p className="font-medium">{doc.filename}</p>
                    <p className="text-sm text-muted-foreground">
                      Uploaded on {new Date(doc.created_at).toLocaleDateString()}
                    </p>
                  </div>
                </div>
                <Button
                  variant="destructive"
                  size="icon"
                  onClick={(e) => {
                    e.stopPropagation(); // Prevent row click when deleting
                    deleteMutation.mutate(doc.id)
                  }}
                  disabled={deleteMutation.isPending && deleteMutation.variables === doc.id}
                >
                  <Trash2 className="h-4 w-4" />
                </Button>
              </li>
            ))}
          </ul>
        ) : (
          <p>You haven't uploaded any documents yet.</p>
        )}
      </CardContent>
    </Card>
  )
}
