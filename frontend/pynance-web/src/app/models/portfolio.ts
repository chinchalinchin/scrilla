import { Holding } from "./holding";

export interface Portfolio{
    holdings: Holding[],
    shares: number[],
    total: number,
    portfolio_return: number,
    portfolio_volatility: number,
}