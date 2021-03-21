export interface Holding{
    ticker: string,
    allocation: number,
    shares: number,
    annual_return: number,
    annual_volatility: number
}

export const mockPortfolio : Holding[] = [
    { ticker: 'ALLY', allocation: 0.2, shares: 1, annual_return: 0.4, annual_volatility: 0.65},
    { ticker: 'BX', allocation: 0.25, shares:2, annual_return: 0.15, annual_volatility: 0.42 },
    { ticker: 'SNE', allocation: 0.4, shares:3, annual_return: 0.33, annual_volatility: 1.02 },
    { ticker: 'PFE', allocation: 0.1, shares:4, annual_return: 0.28, annual_volatility: 0.32 },
    { ticker: 'TWTR', allocation: 0.05, shares: 5, annual_return: 0.41, annual_volatility: 0.44 }
  ]
  