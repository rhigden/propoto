import { cn } from '../utils'

describe('cn utility function', () => {
  it('merges class names correctly', () => {
    const result = cn('text-white', 'bg-black')
    expect(result).toContain('text-white')
    expect(result).toContain('bg-black')
  })

  it('handles conditional classes', () => {
    const isActive = true
    const result = cn('base-class', isActive && 'active-class')
    expect(result).toContain('base-class')
    expect(result).toContain('active-class')
  })

  it('handles false conditional classes', () => {
    const isActive = false
    const result = cn('base-class', isActive && 'active-class')
    expect(result).toContain('base-class')
    expect(result).not.toContain('active-class')
  })

  it('merges conflicting Tailwind classes', () => {
    // Tailwind merge should resolve conflicts
    const result = cn('p-4', 'p-8')
    // Should only contain one padding class (p-8 wins)
    expect(result).toContain('p-8')
    expect(result).not.toContain('p-4')
  })

  it('handles undefined and null values', () => {
    const result = cn('base-class', undefined, null, 'valid-class')
    expect(result).toContain('base-class')
    expect(result).toContain('valid-class')
  })

  it('handles empty strings', () => {
    const result = cn('base-class', '', 'valid-class')
    expect(result).toContain('base-class')
    expect(result).toContain('valid-class')
  })
})




