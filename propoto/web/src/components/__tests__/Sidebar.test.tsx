import { render, screen } from '@testing-library/react'
import { Sidebar } from '../Sidebar'

// Mock next/navigation
jest.mock('next/navigation', () => ({
  usePathname: jest.fn(() => '/dashboard'),
  useRouter: jest.fn(() => ({
    push: jest.fn(),
    replace: jest.fn(),
    prefetch: jest.fn(),
  })),
}))

// Mock the sidebar context
jest.mock('@/lib/sidebar-context', () => ({
  useSidebar: jest.fn(() => ({
    collapsed: false,
    setCollapsed: jest.fn(),
  })),
}))

describe('Sidebar', () => {
  it('renders navigation links', () => {
    render(<Sidebar />)
    
    // The sidebar uses icon-only navigation with title attributes
    const dashboardLink = screen.getByTitle('Dashboard')
    const knowledgeLink = screen.getByTitle('Knowledge')
    const brandLink = screen.getByTitle('Brand')
    const salesLink = screen.getByTitle('Sales')
    const settingsLink = screen.getByTitle('Settings')
    
    expect(dashboardLink).toBeInTheDocument()
    expect(knowledgeLink).toBeInTheDocument()
    expect(brandLink).toBeInTheDocument()
    expect(salesLink).toBeInTheDocument()
    expect(settingsLink).toBeInTheDocument()
  })

  it('renders as a fixed sidebar', () => {
    render(<Sidebar />)
    
    const sidebar = document.querySelector('aside')
    expect(sidebar).toHaveClass('fixed')
    expect(sidebar).toHaveClass('left-0')
  })

  it('highlights active navigation item based on pathname', () => {
    const { usePathname } = require('next/navigation')
    usePathname.mockReturnValue('/dashboard/knowledge')
    
    render(<Sidebar />)
    
    const knowledgeLink = screen.getByTitle('Knowledge')
    // Active links have text-[#ededed] class
    expect(knowledgeLink).toHaveClass('text-[#ededed]')
  })
})
