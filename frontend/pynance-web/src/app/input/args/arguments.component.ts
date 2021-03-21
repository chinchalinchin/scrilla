import { Component, EventEmitter, Input, OnInit, Output } from '@angular/core';
import { FormGroup, FormControl } from '@angular/forms';
import { VirtualTimeScheduler } from 'rxjs';
import { LogService } from 'src/app/services/log.service';
import { containsObject, dateToString, getColumnFromList } from 'src/utilities';

/** ArgumentsComponent
 * DESCRIPTION: 
 * This component is used to parse user input and send it back to the parent 
 *  component in which it is placed. 
 * 
 * INPUT:
 * The ArgumentsComponent has five tags that must be specified as arguments when laying down 
 *  an instance of this component,
 * 
 *  <app-args [tickers]="true" [dates]="true" [target]="true" 
 *            [model]="true" [investment]="true" [method]="true"></app-args>
 * 
 * If these arguments are not provided, they default to false. These arguments configure
 *  which widgets are displayed in the component. If 'tickers' is specified, a text area will
 *  allow users to enter a list of ticker symbols separated by a comma. If 'dates' is specified,
 *  a date picker toggle will allow users to select a start date and end date. If 'target' is
 *  specified a number input field will allow users to enter a decimal. If 'model' is specified,
 *  a drop-down menu will be displayed which will allow users to select from the available pricing
 *  models (Discount Dividend Model, Discount Cashflow Model, etc.)
 * 
 * OUTPUT:
 * The ArgumentsComponent has four output events into which the parent component can wire in 
 *  functions,
 * 
 * <app-args (addTickers)="doThis($event)" (addDates)="doThat($event)" 
 *           (addTarget)="doSomething($event)" (addModel)="doAnything($event)"></app-args>
 * 
 * The 'addTickers' event will contain a string array of ticker symbol list inputted by the user. 
 *  Note, duplicate ticker symbols may exist in this list, so the parent component will have to 
 *  validate the list on its own. 
 * 
 * The 'addDates' event will contain a string array with the start and end date. 
 * 
 * TODOS
 * method: maximize sharpe or minimize volatilty
 **  */

 const PRICING_MODELS=[
   { value:'DDM', viewValue:'Discount Dividend Model' },
   { value:'DCF', viewValue:'Discount Cashflow Model'}
 ]
 const OPTIMIZATION_METHODS=[
   { value: 'MVP', viewValue:'Minimum Variance Portfolio' },
   { value: 'MSR', viewValue: 'Maximize Sharpe Ratio'}
 ]

@Component({
  selector: 'app-args',
  templateUrl: './arguments.component.html'
})
export class ArgumentsComponent implements OnInit {
  // Input: Displayed argument subcomponents
  @Input()
  public tickers : boolean = false;
  @Input()
  public dates : boolean = false;
  @Input()
  public target : boolean = false;
  @Input()
  public model: boolean = false;
  @Input()
  public investment: boolean = false;
  @Input()
  public method: boolean = false;

  // Output: User entered argument values
  @Output()
  private addTickers = new EventEmitter<string[]>();
  @Output()
  private addDates = new EventEmitter<string[]>();
  @Output()
  private addTarget = new EventEmitter<number>();
  @Output()
  private addModel = new EventEmitter<string>();
  @Output()
  private addInvestment = new EventEmitter<number>();
  @Output()
  private addMethod = new EventEmitter<string>();

  public inputTickers: string;
  public inputInvestment: number;
  public inputTarget: number;
  public inputModel: string;
  public inputMethod: string;
  public range = new FormGroup({
    start: new FormControl(),
    end: new FormControl()
  });
  public pricingModels = PRICING_MODELS;
  public optMethods = OPTIMIZATION_METHODS;

  private savedTickers : string[] = [];
  private savedStartDate : Date;
  private savedEndDate : Date;
  private today : Date;
  private location = "app.input.args.ArgumentsComponent"

  constructor(private logs: LogService) { }

  // TODO: query backend for static dropdown list of pricing models
  // TODO: ??? maybe not ??? query backend for static list of optimization methods.
  ngOnInit() {
    this.today = new Date();
  }

  public setStartDate(date) : void {
    this.savedStartDate = date.value;
  }

  public setEndDate(date) : void {
    this.savedEndDate = date.value;
  }

  public saveTickers(){
    this.logs.log('Emitting tickers', this.location)
    let parsedTickers : string[] = this.inputTickers.replace(/\s/g, "").toUpperCase().split(',');
    for(let ticker of parsedTickers){ this.savedTickers.push(ticker); }
    this.addTickers.emit(this.savedTickers);
    this.inputTickers = null;
    this.savedTickers = [];
  }
  
  public saveDates(){
    let emittedDates: string[]
    if(this.savedStartDate){ emittedDates.push(dateToString(this.savedStartDate)); }
    if(this.savedEndDate) { emittedDates.push(dateToString(this.savedEndDate)); }
    if(emittedDates.length>0){ 
      this.logs.log('Emitting dates', this.location);
      this.addDates.emit(emittedDates); 
    }
  }

  public saveInvestment() : void {
    if(this.inputInvestment){
      this.logs.log('Emitting investment', this.location);
      this.addInvestment.emit(this.inputInvestment);
    }
  }

  public saveTarget() : void {
    if(this.inputTarget){
      this.logs.log('Emitting target return', this.location);
      this.addTarget.emit(this.inputTarget);
    }
  }

  public saveModel() : void{
    if(this.inputModel){
      this.logs.log('Emitting valuation model', this.location)
      this.addModel.emit(this.inputModel)
    }
  }

  public saveMethod(event) : void{
    let valueList = getColumnFromList("value", this.optMethods)
    if(containsObject(event.value, valueList)){
      this.logs.log('Emitting optimization method', this.location)
      this.addMethod.emit(event.value)
    }
  }

  public clearInvestment() : void {
    this.inputInvestment = null;
    this.logs.log('Emitting null investment', this.location)
    this.addInvestment.emit(null);
  }

  public clearTarget() : void {
    this.inputTarget = null;
    this.logs.log('Emitting null target return', this.location)
    this.addTarget.emit(null);
  }

  // TODO: emit null dates 

}
