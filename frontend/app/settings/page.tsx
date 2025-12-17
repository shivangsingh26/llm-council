import { APIKeys } from '@/components/settings/api-keys'
import { Preferences } from '@/components/settings/preferences'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'

export default function SettingsPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Settings</h1>
        <p className="text-muted-foreground">
          Configure your LLM Council preferences
        </p>
      </div>

      <Tabs defaultValue="api-keys" className="space-y-6">
        <TabsList>
          <TabsTrigger value="api-keys">API Keys</TabsTrigger>
          <TabsTrigger value="preferences">Preferences</TabsTrigger>
        </TabsList>

        <TabsContent value="api-keys" className="space-y-6">
          <APIKeys />
        </TabsContent>

        <TabsContent value="preferences" className="space-y-6">
          <Preferences />
        </TabsContent>
      </Tabs>
    </div>
  )
}
