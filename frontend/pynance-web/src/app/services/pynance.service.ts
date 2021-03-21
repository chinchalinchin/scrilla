import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable, of } from 'rxjs';
import { LogService } from './log.service';

const ENDPOINTS ={
  optimize:{
    endpoint:'/api/optimize',
    parameters:{
      tickers: 'tickers',
      startDate: 'start',
      endDate: 'end',
      targetReturn: 'target',
      investment: 'invest'
    }
  }
}

@Injectable({
  providedIn: 'root'
})
export class PynanceService {
  private location : string = "app.services.pynance"

  constructor(private logs: LogService,
              private http: HttpClient) { }


  public optimize(): void{
    //TODO
  }

  /**
 * Handle Http operation that failed.
 * Let the app continue.
 * @param operation - name of the operation that failed
 * @param result - optional value to return as the observable result
 */
private handleError<T>(operation = 'operation', result?: T) {
  return (error: any): Observable<T> => {

    // TODO: send the error to remote logging infrastructure
    console.error(error); // log to console instead

    // TODO: better job of transforming error for user consumption
    this.logs.log(`${operation} failed: ${error.message}`, this.location);

    // Let the app keep running by returning an empty result.
    return of(result as T);
  };
}
}
