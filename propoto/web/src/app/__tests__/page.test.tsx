import { render, screen } from '@testing-library/react'
import Home from '../page'

describe('Home Page', () => {
  it('renders main headline', () => {
    render(<Home />)
    
    expect(screen.getByText(/Generate \$10K Proposals/i)).toBeInTheDocument()
    expect(screen.getByText(/in 60 Seconds/i)).toBeInTheDocument()
  })

  it('renders CTA buttons', () => {
    render(<Home />)
    
    expect(screen.getByText('Try It Free')).toBeInTheDocument()
    expect(screen.getByText('See How It Works')).toBeInTheDocument()
    expect(screen.getByText('Launch App')).toBeInTheDocument()
  })

  it('renders stats section', () => {
    render(<Home />)
    
    expect(screen.getByText('60s')).toBeInTheDocument()
    expect(screen.getByText('3x')).toBeInTheDocument()
    expect(screen.getByText('95%')).toBeInTheDocument()
    expect(screen.getByText('Generation Time')).toBeInTheDocument()
    expect(screen.getByText('Close Rate Increase')).toBeInTheDocument()
    expect(screen.getByText('Time Saved')).toBeInTheDocument()
  })

  it('renders feature cards', () => {
    render(<Home />)
    
    expect(screen.getByText('AI-Powered Proposals')).toBeInTheDocument()
    expect(screen.getByText('Visual Presentation Decks')).toBeInTheDocument()
    expect(screen.getByText('Knowledge Intelligence')).toBeInTheDocument()
  })

  it('renders Propoto branding', () => {
    render(<Home />)
    
    const logos = screen.getAllByText('Propoto')
    expect(logos.length).toBeGreaterThan(0)
  })
})


