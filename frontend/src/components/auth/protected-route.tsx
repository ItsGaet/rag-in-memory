"use client"

import { useAuthStore } from "@/store/auth"
import { useRouter } from "next/navigation"
import { useEffect, useState } from "react"

export function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { accessToken } = useAuthStore()
  const router = useRouter()
  const [isClient, setIsClient] = useState(false)

  useEffect(() => {
    setIsClient(true)
  }, [])

  useEffect(() => {
    if (isClient && !accessToken) {
      router.replace("/auth/login")
    }
  }, [accessToken, router, isClient])

  if (!isClient || !accessToken) {
    // You can return a loader here while redirecting
    // This also handles the case where the component is rendered on the server first
    return (
      <div className="flex justify-center items-center h-screen">
        <div>Loading...</div>
      </div>
    )
  }

  return <>{children}</>
}
