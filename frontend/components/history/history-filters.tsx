'use client'

import { useState } from 'react'
import { Input } from '@/components/ui/input'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { Search } from 'lucide-react'
import type { ResearchDomain } from '@/lib/types'

interface HistoryFiltersProps {
  onSearchChange: (query: string) => void
  onDomainChange: (domain: string) => void
}

export function HistoryFilters({
  onSearchChange,
  onDomainChange,
}: HistoryFiltersProps) {
  return (
    <div className="flex flex-col sm:flex-row gap-4">
      <div className="relative flex-1">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
        <Input
          placeholder="Search research history..."
          className="pl-9"
          onChange={(e) => onSearchChange(e.target.value)}
        />
      </div>
      <Select onValueChange={onDomainChange} defaultValue="all">
        <SelectTrigger className="w-full sm:w-[200px]">
          <SelectValue placeholder="Filter by domain" />
        </SelectTrigger>
        <SelectContent>
          <SelectItem value="all">All Domains</SelectItem>
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
  )
}
