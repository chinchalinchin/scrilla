export interface Holding{
    ticker: string,
    allocation: number,
    return: number,
    volatility: number
}

export const mockPortfolio : Holding[] = [
    { ticker: 'ALLY', allocation: 0.2, return: 0.4, volatility: 0.65},
    { ticker: 'BX', allocation: 0.25, return: 0.15, volatility: 0.42 },
    { ticker: 'SNE', allocation: 0.4, return: 0.33, volatility: 1.02 },
    { ticker: 'PFE', allocation: 0.1, return: 0.28, volatility: 0.32 },
    { ticker: 'TWTR', allocation: 0.05, return: 0.41, volatility: 0.44 }
  ]
  