import { Holding } from "./holding";

export interface Portfolio{
    holdings: Holding[],
    total: number,
    portfolio_return: number,
    portfolio_volatility: number,
}