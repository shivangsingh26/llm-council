'use client'

import { useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Button } from '@/components/ui/button'
import { Eye, EyeOff, Save } from 'lucide-react'
import { toast } from 'sonner'

export function APIKeys() {
  const [showKeys, setShowKeys] = useState({
    openai: false,
    gemini: false,
    deepseek: false,
  })

  const [keys, setKeys] = useState({
    openai: '',
    gemini: '',
    deepseek: '',
  })

  const handleSave = () => {
    // TODO: Implement actual save logic in Phase 4
    localStorage.setItem('api_keys', JSON.stringify(keys))
    toast.success('API keys saved successfully')
  }

  const toggleVisibility = (key: keyof typeof showKeys) => {
    setShowKeys((prev) => ({ ...prev, [key]: !prev[key] }))
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>API Keys</CardTitle>
        <CardDescription>
          Configure your API keys for the different AI models
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* OpenAI */}
        <div className="space-y-2">
          <Label htmlFor="openai-key">OpenAI API Key</Label>
          <div className="flex gap-2">
            <div className="relative flex-1">
              <Input
                id="openai-key"
                type={showKeys.openai ? 'text' : 'password'}
                placeholder="sk-..."
                value={keys.openai}
                onChange={(e) =>
                  setKeys((prev) => ({ ...prev, openai: e.target.value }))
                }
              />
              <Button
                variant="ghost"
                size="sm"
                className="absolute right-0 top-0 h-full px-3"
                onClick={() => toggleVisibility('openai')}
              >
                {showKeys.openai ? (
                  <EyeOff className="h-4 w-4" />
                ) : (
                  <Eye className="h-4 w-4" />
                )}
              </Button>
            </div>
          </div>
          <p className="text-xs text-muted-foreground">
            Get your API key from{' '}
            <a
              href="https://platform.openai.com/api-keys"
              target="_blank"
              rel="noopener noreferrer"
              className="text-primary hover:underline"
            >
              OpenAI Platform
            </a>
          </p>
        </div>

        {/* Google Gemini */}
        <div className="space-y-2">
          <Label htmlFor="gemini-key">Google Gemini API Key</Label>
          <div className="flex gap-2">
            <div className="relative flex-1">
              <Input
                id="gemini-key"
                type={showKeys.gemini ? 'text' : 'password'}
                placeholder="AIza..."
                value={keys.gemini}
                onChange={(e) =>
                  setKeys((prev) => ({ ...prev, gemini: e.target.value }))
                }
              />
              <Button
                variant="ghost"
                size="sm"
                className="absolute right-0 top-0 h-full px-3"
                onClick={() => toggleVisibility('gemini')}
              >
                {showKeys.gemini ? (
                  <EyeOff className="h-4 w-4" />
                ) : (
                  <Eye className="h-4 w-4" />
                )}
              </Button>
            </div>
          </div>
          <p className="text-xs text-muted-foreground">
            Get your API key from{' '}
            <a
              href="https://makersuite.google.com/app/apikey"
              target="_blank"
              rel="noopener noreferrer"
              className="text-primary hover:underline"
            >
              Google AI Studio
            </a>
          </p>
        </div>

        {/* DeepSeek */}
        <div className="space-y-2">
          <Label htmlFor="deepseek-key">DeepSeek API Key</Label>
          <div className="flex gap-2">
            <div className="relative flex-1">
              <Input
                id="deepseek-key"
                type={showKeys.deepseek ? 'text' : 'password'}
                placeholder="sk-..."
                value={keys.deepseek}
                onChange={(e) =>
                  setKeys((prev) => ({ ...prev, deepseek: e.target.value }))
                }
              />
              <Button
                variant="ghost"
                size="sm"
                className="absolute right-0 top-0 h-full px-3"
                onClick={() => toggleVisibility('deepseek')}
              >
                {showKeys.deepseek ? (
                  <EyeOff className="h-4 w-4" />
                ) : (
                  <Eye className="h-4 w-4" />
                )}
              </Button>
            </div>
          </div>
          <p className="text-xs text-muted-foreground">
            DeepSeek API configuration (local or hosted)
          </p>
        </div>

        <Button onClick={handleSave} className="w-full">
          <Save className="mr-2 h-4 w-4" />
          Save API Keys
        </Button>
      </CardContent>
    </Card>
  )
}
