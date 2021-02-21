import { MatTable } from '@angular/material';
import { Component, Input, OnInit, QueryList, SimpleChanges, ViewChild, ViewChildren } from '@angular/core';
import {FormGroup, FormControl} from '@angular/forms';
import { Holding } from 'src/app/models/holding';
import { containsObject, removeStringFromArray } from 'src/utilities';
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
  range = new FormGroup({
    start: new FormControl(),
    end: new FormControl()
  });

  private clearDisabled : boolean = true;
  private portfolio : Holding[] = [];
  private displayedColumns: string[] = [];
  private today: Date  = new Date();

  @ViewChild('portfolioTable', {static: false})
  private portfolioTable : MatTable<Holding[]>;
  @ViewChild(TickerComponent, {static: false}) 
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
          this.displayedColumns = ['index', 'ticker']
          for(let holding of this.portfolio){
            holding.allocation = null;
          }
        }
        // allocation portfolio passed in
        else{
          this.displayedColumns = ['index', 'ticker', 'allocation']
          for(let newAllocation of changes.allocations.currentValue){
            let tickerIndex=changes.allocations.currentValue.indexOf(newAllocation)
            this.portfolio[tickerIndex].allocation = newAllocation
          }
        }
      }
    }

  }

  public setTickers(tickers: string[]) : void{
    for(let holding of this.portfolio){
      if(containsObject(holding.ticker, tickers)){
        removeStringFromArray(holding.ticker, tickers)
      }
    }

    for(let ticker of tickers){
      this.portfolio.push({ ticker: ticker, allocation: null, return: null, volatility: null})
    }
  
    if(this.portfolio.length != 0){
      this.clearDisabled = false;
      this.displayedColumns = ['index', 'ticker']
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
