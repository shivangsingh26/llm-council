'use client'

import { useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Label } from '@/components/ui/label'
import { Switch } from '@/components/ui/switch'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { Button } from '@/components/ui/button'
import { Download, Save } from 'lucide-react'
import { toast } from 'sonner'

export function Preferences() {
  const [preferences, setPreferences] = useState({
    defaultDomain: 'general',
    maxTokens: '500',
    saveHistory: true,
    autoExport: false,
  })

  const handleSave = () => {
    localStorage.setItem('preferences', JSON.stringify(preferences))
    toast.success('Preferences saved successfully')
  }

  const handleExport = () => {
    // TODO: Implement actual export logic
    const data = {
      preferences,
      exported_at: new Date().toISOString(),
    }
    const blob = new Blob([JSON.stringify(data, null, 2)], {
      type: 'application/json',
    })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `llm-council-settings-${Date.now()}.json`
    a.click()
    URL.revokeObjectURL(url)
    toast.success('Settings exported successfully')
  }

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>Preferences</CardTitle>
          <CardDescription>
            Customize your LLM Council experience
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Default Domain */}
          <div className="space-y-2">
            <Label htmlFor="default-domain">Default Research Domain</Label>
            <Select
              value={preferences.defaultDomain}
              onValueChange={(value) =>
                setPreferences((prev) => ({ ...prev, defaultDomain: value }))
              }
            >
              <SelectTrigger id="default-domain">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="general">General</SelectItem>
                <SelectItem value="technology">Technology</SelectItem>
                <SelectItem value="science">Science</SelectItem>
                <SelectItem value="business">Business</SelectItem>
                <SelectItem value="health">Health</SelectItem>
                <SelectItem value="sports">Sports</SelectItem>
                <SelectItem value="entertainment">Entertainment</SelectItem>
              </SelectContent>
            </Select>
          </div>

          {/* Max Tokens */}
          <div className="space-y-2">
            <Label htmlFor="max-tokens">Default Max Tokens</Label>
            <Select
              value={preferences.maxTokens}
              onValueChange={(value) =>
                setPreferences((prev) => ({ ...prev, maxTokens: value }))
              }
            >
              <SelectTrigger id="max-tokens">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="250">250 tokens</SelectItem>
                <SelectItem value="500">500 tokens</SelectItem>
                <SelectItem value="1000">1000 tokens</SelectItem>
                <SelectItem value="2000">2000 tokens</SelectItem>
              </SelectContent>
            </Select>
          </div>

          {/* Save History */}
          <div className="flex items-center justify-between">
            <div className="space-y-0.5">
              <Label htmlFor="save-history">Save Research History</Label>
              <p className="text-sm text-muted-foreground">
                Automatically save all research sessions
              </p>
            </div>
            <Switch
              id="save-history"
              checked={preferences.saveHistory}
              onCheckedChange={(checked) =>
                setPreferences((prev) => ({ ...prev, saveHistory: checked }))
              }
            />
          </div>

          {/* Auto Export */}
          <div className="flex items-center justify-between">
            <div className="space-y-0.5">
              <Label htmlFor="auto-export">Auto Export Results</Label>
              <p className="text-sm text-muted-foreground">
                Automatically export results after each research
              </p>
            </div>
            <Switch
              id="auto-export"
              checked={preferences.autoExport}
              onCheckedChange={(checked) =>
                setPreferences((prev) => ({ ...prev, autoExport: checked }))
              }
            />
          </div>

          <Button onClick={handleSave} className="w-full">
            <Save className="mr-2 h-4 w-4" />
            Save Preferences
          </Button>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Export Settings</CardTitle>
          <CardDescription>
            Download your settings and preferences
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Button onClick={handleExport} variant="outline" className="w-full">
            <Download className="mr-2 h-4 w-4" />
            Export Settings as JSON
          </Button>
        </CardContent>
      </Card>
    </div>
  )
}
