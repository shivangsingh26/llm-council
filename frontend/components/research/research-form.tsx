'use client'

import { zodResolver } from '@hookform/resolvers/zod'
import { useForm } from 'react-hook-form'
import * as z from 'zod'
import { Button } from '@/components/ui/button'
import {
  Form,
  FormControl,
  FormDescription,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from '@/components/ui/form'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { Textarea } from '@/components/ui/textarea'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Loader2 } from 'lucide-react'
import type { ResearchRequest } from '@/lib/types'

const formSchema = z.object({
  query: z.string().min(10, {
    message: 'Query must be at least 10 characters.',
  }),
  domain: z.enum([
    'sports',
    'finance',
    'shopping',
    'healthcare',
  ]),
  max_tokens: z.number().optional(),
})

interface ResearchFormProps {
  onSubmit: (data: ResearchRequest) => void
  isLoading: boolean
}

export function ResearchForm({ onSubmit, isLoading }: ResearchFormProps) {
  const form = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      query: '',
      domain: 'healthcare',
      max_tokens: 500,
    },
  })

  return (
    <Card>
      <CardHeader>
        <CardTitle>New Research Query</CardTitle>
      </CardHeader>
      <CardContent>
        <Form {...form}>
          <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
            <FormField
              control={form.control}
              name="domain"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Research Domain</FormLabel>
                  <Select
                    onValueChange={field.onChange}
                    defaultValue={field.value}
                  >
                    <FormControl>
                      <SelectTrigger>
                        <SelectValue placeholder="Select a domain" />
                      </SelectTrigger>
                    </FormControl>
                    <SelectContent>
                      <SelectItem value="healthcare">Healthcare</SelectItem>
                      <SelectItem value="sports">Sports</SelectItem>
                      <SelectItem value="finance">Finance</SelectItem>
                      <SelectItem value="shopping">Shopping</SelectItem>
                    </SelectContent>
                  </Select>
                  <FormDescription>
                    Choose the domain that best fits your query
                  </FormDescription>
                  <FormMessage />
                </FormItem>
              )}
            />

            <FormField
              control={form.control}
              name="query"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Research Query</FormLabel>
                  <FormControl>
                    <Textarea
                      placeholder="Enter your research question here..."
                      className="min-h-[120px]"
                      {...field}
                    />
                  </FormControl>
                  <FormDescription>
                    Ask a detailed question to get comprehensive insights
                  </FormDescription>
                  <FormMessage />
                </FormItem>
              )}
            />

            <Button type="submit" className="w-full" disabled={isLoading}>
              {isLoading ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Researching...
                </>
              ) : (
                'Start Research'
              )}
            </Button>
          </form>
        </Form>
      </CardContent>
    </Card>
  )
}
