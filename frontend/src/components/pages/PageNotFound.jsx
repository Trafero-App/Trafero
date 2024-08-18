import {useNavigate} from 'react-router-dom'

const PageNotFound = () => {
  const navigate=useNavigate()
  return (
    <div className='h-full flex flex-wrap justify-center'>
      <div className='flex flex-col justify-center mr-10'>
        <h1 className='font-bold text-5xl pb-1'>404</h1>
        <h1>Oops! Page Not Found!</h1>
        <button className='hover:underline rounded-md mt-5 font-bold' onClick={()=>navigate('/map')}>Click here to go back to Main Page</button>
      </div>
      <h1 className='flex items-center ml-10 text-9xl'>:(</h1>
    </div>
    
  )
}

export default PageNotFound