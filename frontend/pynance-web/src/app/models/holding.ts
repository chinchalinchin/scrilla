export interface Holding{
    ticker: string,
    allocation: number,
    shares: number,
    annual_return: number,
    annual_volatility: number,
    sharpe_ratio: number,
    asset_beta: number,
    discount_dividend: number;
}

export const mockPortfolio : Holding[] = [
    { ticker: 'ALLY', allocation: 0.2, shares: 1, annual_return: 0.4, 
        annual_volatility: 0.65, sharpe_ratio: 0.2, asset_beta: 1.1, discount_dividend: 40 },
    { ticker: 'BX', allocation: 0.25, shares:2, annual_return: 0.15, 
        annual_volatility: 0.42, sharpe_ratio: 0.3, asset_beta: 0.8, discount_dividend: 30.56 },
    { ticker: 'SNE', allocation: 0.4, shares:3, annual_return: 0.33, 
        annual_volatility: 1.02, sharpe_ratio: 0.3, asset_beta: 0.66, discount_dividend: 26.75 },
    { ticker: 'PFE', allocation: 0.1, shares:4, annual_return: 0.28, 
        annual_volatility: 0.32, sharpe_ratio: 2.28, asset_beta: 2.3, discount_dividend: 117.34 },
    { ticker: 'TWTR', allocation: 0.05, shares: 5, annual_return: 0.41, 
        annual_volatility: 0.44, sharpe_ratio: 1.12, asset_beta: 1, discount_dividend: 47.77 }
  ]
  