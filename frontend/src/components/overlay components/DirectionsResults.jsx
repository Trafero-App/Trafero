import {IoIosArrowBack} from 'react-icons/io'
import { ClipLoader } from 'react-spinners'
import DirectionsRouteItem from './DirectionsRouteItem'
import DirectionsChainRouteItem from './DirectionsChainRouteItem'

const length = (directionsResults) => {
    var len=0
    directionsResults.forEach((e) => {
        if(e.chain) len++
        len++
    })
    return len
}

const DirectionsResults = ({
    directionsResults, areDirectionsResultsLoading,
    startingPoint, destination,
    setChosenBusIds, setDirectionsResultsLoading,
    previewedIds, setPreviewedIds
}) => {
    return (
        <div 
        className='pointer-events-auto w-full max-w-96 rounded-xl bg-white shadow-md'
        >
            <div 
            className='text-gray4 flex items-center h-14 lg:h-12 border-b-2 border-gray2'
            style={{cursor: 'pointer'}}
            onClick={() =>{
                setChosenBusIds(null)
                setDirectionsResultsLoading(false)
            }}
            >
                <IoIosArrowBack
                className='mx-2 h-8 w-8 lg:h-7 lg:w-7 text-gray4'
                />
                <h1 className='text-[18px] lg:text-[16px]'>Back to Directions</h1>
            </div>
            <div className='my-3'>
                {areDirectionsResultsLoading ?
                <div className='flex justify-center items-center'>
                    <ClipLoader size='29px' color='#C8C8C8'/>
                </div>
                
                :
                directionsResults.length==0 ?
                <div className='h-[29px] flex justify-center items-center'>
                    <h1 className='text-gray4 text-md'>No results found.</h1>
                </div>
                :
                <div className={length(directionsResults)>3 ? 'scrollable h-36' : ''}>
                    {
                    directionsResults.map((element,index) => 
                    !element.chain ?
                    <DirectionsRouteItem 
                    key={index} 
                    routeData={element} 
                    startingPoint={startingPoint} 
                    destination={destination}
                    previewedIds={previewedIds}
                    setPreviewedIds={setPreviewedIds}
                    />
                    :
                    <DirectionsChainRouteItem 
                    key={index} 
                    routeData={element}
                    previewedIds={previewedIds}
                    setPreviewedIds={setPreviewedIds}
                    />
                    )
                    }
                </div>
                }
            </div>
        </div>
    )
}

export default DirectionsResults