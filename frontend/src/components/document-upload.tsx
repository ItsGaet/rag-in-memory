"use client"

import { useState } from "react"
import { useMutation, useQueryClient } from "@tanstack/react-query"
import { toast } from "sonner"
import { Upload } from "lucide-react"

import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"

const uploadDocument = async (file: File) => {
  const formData = new FormData()
  formData.append("file", file)

  // We can't use our fetchApi wrapper directly because it's for JSON.
  // We need to use fetch directly for FormData.
  const { accessToken } = useAuthStore.getState()
  const response = await fetch('/api/v1/documents/', {
    method: 'POST',
    headers: {
      ...(accessToken && { Authorization: `Bearer ${accessToken}` }),
    },
    body: formData,
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'File upload failed');
  }

  return response.json();
};

// I need to import useAuthStore
import { useAuthStore } from "@/store/auth";

export function DocumentUpload() {
  const [file, setFile] = useState<File | null>(null)
  const queryClient = useQueryClient()

  const mutation = useMutation({
    mutationFn: uploadDocument,
    onSuccess: () => {
      toast.success("Document uploaded successfully!")
      setFile(null)
      // Invalidate the documents query to refetch the list
      queryClient.invalidateQueries({ queryKey: ['documents'] })
    },
    onError: (error: Error) => {
      toast.error(error.message)
    },
  })

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      setFile(e.target.files[0])
    }
  }

  const handleUpload = () => {
    if (file) {
      mutation.mutate(file)
    } else {
      toast.warning("Please select a file first.")
    }
  }

  return (
    <div className="flex items-center gap-2">
      <Input type="file" onChange={handleFileChange} className="max-w-xs" />
      <Button onClick={handleUpload} disabled={!file || mutation.isPending}>
        <Upload className="mr-2 h-4 w-4" />
        {mutation.isPending ? "Uploading..." : "Upload"}
      </Button>
    </div>
  )
}
