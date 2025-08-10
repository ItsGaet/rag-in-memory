"use client"

import { useQuery } from "@tanstack/react-query"
import { fetchApi } from "@/lib/api"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"

// This is a placeholder for fetching user data
const getUser = async () => {
  // This endpoint requires authentication. We'll need to handle tokens.
  // For now, let's assume the browser's cookies handle the session.
  try {
    const data = await fetchApi('/users/me');
    return data;
  } catch (error) {
    // This will likely fail if we don't handle auth tokens,
    // which we haven't yet. We'll need to implement token storage
    // and sending it with requests.
    console.error("Failed to fetch user", error);
    return null;
  }
};


export default function DashboardPage() {
  const { data: user, isLoading, error } = useQuery({
    queryKey: ['user'],
    queryFn: getUser,
  })

  return (
    <div>
      <h1 className="text-3xl font-bold mb-4">Dashboard</h1>
      <Card>
        <CardHeader>
          <CardTitle>Welcome!</CardTitle>
        </CardHeader>
        <CardContent>
          {isLoading && <p>Loading user data...</p>}
          {error && <p className="text-red-500">Could not load user data. Are you logged in?</p>}
          {user && (
            <div>
              <p>Welcome back, <strong>{user.full_name || user.email}</strong>!</p>
              <p className="text-sm text-muted-foreground">You are now ready to chat with your documents.</p>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
