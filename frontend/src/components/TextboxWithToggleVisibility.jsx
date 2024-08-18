import {IoMdEye,IoMdEyeOff} from 'react-icons/io'

// need these states
// const [password,setPassword] = useState('')
// const [passwordVisible, setPasswordVisible] = useState(false);
// const [passwordFocused, setPasswordFocused] = useState(false);

// use it like this
{/*     <TextboxWithToggleVisibility
          password={password}
          setPassword={setPassword}
          passwordFocused={passwordFocused}
          setPasswordFocused={setPasswordFocused}
          passwordVisible={passwordVisible}
          setPasswordVisible={setPasswordVisible}
        /> */}

const TextboxWithToggleVisibility = ({
    password, setPassword,
    passwordVisible, setPasswordVisible,
    className=""
}) => {
    return (
        <div className={'relative '+className}>
          <input
          id='password-field'
          value={password}
          type={passwordVisible ? 'text' : 'password'}
          className="w-full px-4 py-2 rounded-xl bg-gray1 focus:outline-none placeholder-gray4" 
          placeholder='Password'
          onChange={e => setPassword(e.target.value)}
          >
          </input>
          <div
              className="absolute bottom-1/2 right-3 translate-y-3"
              onClick={() => {setPasswordVisible(!passwordVisible)}}
              style={{cursor: 'pointer'}}
            >
              {passwordVisible ? <IoMdEyeOff className='w-6 h-6 text-gray4'/> : <IoMdEye className='w-6 h-6 text-gray4'/>}
          </div>
        </div>
    )
} 
export default TextboxWithToggleVisibility