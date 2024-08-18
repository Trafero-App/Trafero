import {IoMdInformationCircleOutline} from 'react-icons/io'

const minutesToText= (minutes) => {
  if(minutes==0) return '0m'
  if(minutes%60==0) return `${Math.floor(minutes/60)}h`
  if(minutes<60) return `${minutes}m`
  return `${Math.floor(minutes/60)}h ${minutes%60}m`
}


const ExpectedTimeCard = ({
    expectedTime,
    isExpectedTimeLoading
}) => {
  return (
    <div
    className='text-sm truncate text-white mb-3 pointer-events-auto w-full max-w-96 flex justify-between items-center h-8 lg:h-7 rounded-xl bg-blue3 opacity-90 hover:opacity-100 shadow-md'
    >
        <div className='h-8 w-8 lg:h-7 lg:w-7 flex items-center justify-center'>
            <IoMdInformationCircleOutline className='h-5 w-5 lg:h-4 lg-w-4'/>
        </div>
        {(expectedTime==null && !isExpectedTimeLoading) ?
        <h1>Click on the route to choose your pickup spot</h1>
        : 
        isExpectedTimeLoading && expectedTime==null ?
        <h1>Calculating ETA...</h1>
        : 
        <h1>Expected time till arrival: {minutesToText(expectedTime)}</h1>
        }
        <div className='h-8 w-8 lg:h-7 lg:w-7'>
        </div>
    </div>
  )
}

export default ExpectedTimeCard