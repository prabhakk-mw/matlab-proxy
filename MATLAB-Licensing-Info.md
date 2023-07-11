# MATLAB Licensing Info

**Table of Contents**
1. [Selecting a Licensing Option](#selecting-a-licensing-option)
    1. [Online License Manager](#online-license-manager)
    2. [Network License Manager](#network-license-manager)
       1. [Locating your License Administrator](#locating-your-license-administrator)
    4. [Existing License](#existing-license)
2.[For Administrators](#for-administrators)

## Selecting a Licensing Option 
`matlab-proxy` provides multiple options to license the MATLAB session that it spawns.

When `matlab-proxy-app` is run for the first time, the following licensing screen is presented:

<p align="left">
  <img width="600" src="img/licensing_GUI.png">
</p>

The three licensing options presented in each of the tabs above are:
1. Online License Manager
2. Network License Manager
3. Existing License

### Online License Manager
![image](https://github.com/prabhakk-mw/matlab-proxy/assets/64955767/026b5728-5494-4275-a4db-cf21a6888337)

Use this tab, when your MathWorks Account is configured with licenses for use with [Online Licensing]([url](https://in.mathworks.com/products/matlab-parallel-server/online-licensing.html)).

Enter your the email address associated with your MathWorks Account and follow the on screen instructions to start MATLAB with your license configured with Online Licensing.

The licenses that are suitable for use with Online Licensing are:
* Individual
* Home
* Student
* Campus-Wide Licenses

If you are an academic user, you can use [this tool](https://www.mathworks.com/academia/tah-support-program/eligibility.html) to determine if you have access to a campus-wide license through your institution. Otherwise, to see the licenses linked to your account, log in to your MathWorks account and go to [License Center](https://www.mathworks.com/licensecenter/?s_tid=hp_ff_s_license). You can link your MathWorks account with a license using [this tool](https://www.mathworks.com/licensecenter/licenses/add).

[Note to self]: look to provide useful links to Online Licensing information, things like how to configure, install or setup an account with it. For example: https://in.mathworks.com/products/matlab-parallel-server/online-licensing.html

### Network License Manager
![image](https://github.com/prabhakk-mw/matlab-proxy/assets/64955767/72925e3c-76f3-4aa5-8bab-0fdda4abade3)

Use this tab, when your organization has a Network License Manager configured. 
Contact your organization's **license administrator*** to find the address for the network license manager.

The address of the network license manager is specified in the following form of `port@hostname` as shown in the example below:
```bash
27000@MyServerName.example.com
```
The following links provide more information related to this option:
* [Configuring a Network License Manager](https://www.mathworks.com/help/install/administer-network-licenses.html)
* Alternatively, one can leverage this option programatically using the environment variable `MLM_LICENSE_FILE` as shown in [Advanced-Usage.md](https://github.com/mathworks/matlab-proxy/blob/main/Advanced-Usage.md)

The licenses that are suitable for use with Network Licensing are:
* Concurrent
* Network Named User
* Campus Wide Licenses

#### Locating your License Administrator
To find your license administrator:
1. Sign in to your [MathWorks Account](https://www.mathworks.com/mwaccount/)
2. Click the license you are using
3. Then click the tab marked “Contact Administrators”.

### Existing License
![image](https://github.com/prabhakk-mw/matlab-proxy/assets/64955767/3c0b2328-8162-466d-b6c2-648fcd225dd7)

This tab can be used when `matlab-proxy-app` is running on a machine in which MATLAB has already been installed and activated.
Use this option after verifying that `matlab` can launch on the machine without providing any licensing information.
For example, running the following a terminal on a machine with MATLAB installed:
```bash
matlab -nojvm
```
should bring the MATLAB command prompt up successfully.

When MATLAB is launched using this tab, `matlab-proxy` will:
1. Not look for any licensing information and;
2. Will attempt to launch `matlab` directly without providing any additional information to MATLAB related to licensing.

## For Administrators
This section is for the administrators who are configure environments to providing access to MATLAB through the `matlab-proxy`.

1. Administrators who want to provide `Online Licensing` should contact Mathworks Licensing & Support to configure this for their users.
2. Administrators who want to provide licenses administered through a `Network License Manager`:
   1. Refer to [Configuring a Network License Manager](https://www.mathworks.com/help/install/administer-network-licenses.html)
   2. Once configured, you can either:
      1. Provide the address and port number on which the license server is running to your users.
      2. Preconfigure your users environment with the environment variable `MLM_LICENSE_FILE` such that it is set with the `port@hostname` pointing to your server.
