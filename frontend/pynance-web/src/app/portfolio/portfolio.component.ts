import { MatTable } from '@angular/material/table';
import { Component, Input, OnInit, QueryList, SimpleChanges, ViewChild, ViewChildren } from '@angular/core';
import { Holding } from 'src/app/models/holding';
import { containsObject } from 'src/utilities';
import { TickerComponent } from '../ticker/ticker.component';

const mockPortfolio : Holding[] = [
  { ticker: 'ALLY', allocation: 0.2, return: 0.4, volatility: 0.65},
  { ticker: 'BX', allocation: 0.25, return: 0.15, volatility: 0.42 },
  { ticker: 'SNE', allocation: 0.4, return: 0.33, volatility: 1.02 },
  { ticker: 'PFE', allocation: 0.1, return: 0.28, volatility: 0.32 },
  { ticker: 'TWTR', allocation: 0.05, return: 0.41, volatility: 0.44 }
]

@Component({
  selector: 'app-portfolio',
  templateUrl: './portfolio.component.html'
})
/**
 * PortfolioComponent
 * 
 * Input
 * 1. allocations: [number]. An ordered array of portfolio allocation corresponding to the 
 *    the tickers initialized in the portfolio. 
 */
export class PortfolioComponent implements OnInit {

  public portfolio : Holding[] = [];
  public clearDisabled : boolean = true;
  public displayedColumns: string[] = [];
  private today: Date  = new Date();

  @ViewChild('portfolioTable')
  private portfolioTable : MatTable<Holding[]>;
  @ViewChild('tickerInput') 
  private tickerChild: TickerComponent;

  @Input()
  private allocations: number[]

  ngOnInit() { 
    console.log(`tickerChild ${this.tickerChild}`)
   } 
  
  ngOnChanges(changes: SimpleChanges) {
    console.log(`changes ${changes}`)
    
    if (changes.allocations) {
      if(this.portfolio.length != 0){
        // empty portfolio passed in
        if(changes.allocations.currentValue.length == 0){ 
          this.displayedColumns = [ 'ticker' ]
          for(let holding of this.portfolio){
            holding.allocation = null;
          }
        }
        // allocation portfolio passed in
        else{
          this.displayedColumns = [ 'ticker', 'allocation']
          for(let newAllocation of changes.allocations.currentValue){
            let tickerIndex=changes.allocations.currentValue.indexOf(newAllocation)
            this.portfolio[tickerIndex].allocation = newAllocation
          }
        }
      }
    }

  }

  public getTickers(): string[]{
    let tickers : string [] = []
    for(let holding of this.portfolio){
      tickers.push(holding.ticker)
    }
    return tickers;
  }

  public setTickers(inputTickers: string[]) : void{
    let unduplicatedTickers : string[] = [];
    let portfolioTickers : string[] = this.getTickers();
    
    for(let ticker of inputTickers){
      if(!containsObject(ticker, portfolioTickers)){
        unduplicatedTickers.push(ticker);
      }
    }

    for(let ticker of unduplicatedTickers){
      this.portfolio.push({ ticker: ticker, allocation: null, return: null, volatility: null})
    }
  
    if(this.portfolio.length != 0){
      this.clearDisabled = false;
      this.displayedColumns = [ 'ticker' ]
    }
    
    this.portfolioTable.renderRows()

  }

  public setAllocations(allocations : number[]) : void{
    for(let portion of allocations){
      let thisIndex : number = allocations.indexOf(portion)
      this.portfolio[thisIndex].allocation = portion
    }
  }

  public clearPortfolio() : void{
    this.portfolio = [];
    this.clearDisabled = true;
    this.displayedColumns = [];
  }

}
