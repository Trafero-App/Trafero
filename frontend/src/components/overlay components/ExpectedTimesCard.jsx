import {IoMdInformationCircleOutline} from 'react-icons/io'

const minutesToText= (minutes) => {
  if(minutes==0) return '0m'
  if(minutes%60==0) return `${Math.floor(minutes/60)}h`
  if(minutes<60) return `${minutes}m`
  return `${Math.floor(minutes/60)}h ${minutes%60}m`
}

const ExpectedTimesCard = ({
    expectedTimes,
    areExpectedTimesLoading
}) => {
  return (
    <div
    className='text-sm truncate text-white mb-3 pointer-events-auto w-full max-w-96 flex justify-between items-center h-8 lg:h-7 rounded-xl bg-blue3 opacity-90 hover:opacity-100 shadow-md'
    >
        <div className='h-8 w-8 lg:h-7 lg:w-7 flex items-center justify-center'>
            <IoMdInformationCircleOutline className='h-5 w-5 lg:h-4 lg-w-4'/>
        </div>
        {(expectedTimes==null && !areExpectedTimesLoading) ?
        <h1>Click on the route to choose your pickup spot</h1>
        : 
        areExpectedTimesLoading ?
        <h1>Calculating ETA...</h1>
        : 
        expectedTimes.length==0 ?
        <h1>There are no vehicles currently on this route</h1>
        :
        (expectedTimes[0].passed) ? 
        <h1>There are no busses that will reach this point</h1>
        :
        <h1>{`The closest vehicle is ${minutesToText(expectedTimes[0].expected_time)} away`}</h1>
        }
        <div className='h-8 w-8 lg:h-7 lg:w-7'>
        </div>
    </div>
  )
}

export default ExpectedTimesCard